# Create your views here.
import csv
import datetime
import json
import smtplib
from email.mime.image import MIMEImage
from random import randint

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.contrib.sessions.models import Session
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError, connection
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

# Test function for this view
from vote.models import Voter, College, Candidate, ElectionStatus, Vote, Position, Issue, BasePosition, Unit, Poll, ElectionState, Election

# EMAIL BODY CONST
fp = open(settings.BASE_DIR + '/email_template.html', 'r')
HTML_STR = fp.read()
fp.close()

# TODO: Make this async to message
def send_email(voter_id, voter_key = None):
    if voter_key == None:
        voter_key = PasscodeView.generate_passcode()

        user = User.objects.get(username=voter_id)
        user.set_password(voter_key)
        user.save()

    voter_email = voter_id + '@dlsu.edu.ph'

    # Create email with message and template
    # Imbedded Image
    fp = open(settings.BASE_DIR + '/ComelecLogo.png', 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    img.add_header('Content-ID', '<logo>')

    subject = '[COMELEC] Election is now starting'
    text = '''\
DLSU Comelec is inviting to you to vote in the elections.
Voter ID: {}
Voter Key: {}
To vote, go to this link: https://some_link
    '''.format(voter_id, voter_key)

    html = HTML_STR
    html = html.replace('11xxxxxx', voter_id, 2)
    html = html.replace('xxxxxxxx', voter_key, 1)

    msg = EmailMultiAlternatives(
        subject = subject,
        body = text,
        from_email = settings.EMAIL_HOST_USER,
        to = [ voter_email ]
    )
    msg.attach_alternative(html, "text/html")
    msg.attach(img)
    msg.send()

def officer_test_func(user):
    try:
        return Group.objects.get(name='comelec') in user.groups.all()
    except Group.DoesNotExist:
        return False


class RestrictedView(UserPassesTestMixin, View):
    # Check whether the user accessing this page is a system administrator or not
    def test_func(self):
        return officer_test_func(self.request.user)


class OfficerView(RestrictedView):
    template_name = ''

    # Defines the number of objects shown in a page
    objects_per_page = 5

    # Display the necessary objects for a specific context
    def display_objects(self, page, query=False):
        pass

    def get(self, request):
        pass

    def post(self, request):
        pass


class VotersView(OfficerView):
    template_name = 'officer/officer-voter.html'

    # A convenience function for creating a voter
    @staticmethod
    def create_voter(first_name, last_name, username, college_name, voting_status_name, eligibility_status_name):
        # Save the names in title case
        first_name = first_name.title()
        last_name = last_name.title()

        # Derive the email from the username (the ID number)
        email = username + '@dlsu.edu.ph'

        # Set an initial password
        password = PasscodeView.generate_passcode()

        # Retrieve the voting and eligibility statuses using the name provided
        voting_status = True if voting_status_name == 'Has already voted' else False
        eligibility_status = True if eligibility_status_name == 'Eligible' else False

        # Create the user given the information provided
        user = User.objects.create_user(username=username, email=email, first_name=first_name,
                                        last_name=last_name,
                                        password=password)

        # Add the user to the voter group
        group = Group.objects.get(name='voter')
        group.user_set.add(user)

        # Save the changes to the created user
        user.save()

        # Retrieve the college using the name provided
        college = College.objects.get(name=college_name)

        # Create the voter using the created user
        Voter.objects.create(user=user, college=college,
                             voting_status=voting_status, eligibility_status=eligibility_status)
        
        election_state = ResultsView.get_election_state()

        if (election_state == ElectionState.ONGOING.value or election_state == ElectionState.PAUSED.value) \
                and not voting_status and eligibility_status:
            # Also check if his batch and college is in the election status
            if ElectionStatus.objects.filter(college=college, batch=int(username[:3])).count() > 0:
                 # Init email server
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                server.ehlo()
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                send_email(username, password)
                print('Email sent to ' + username)
                # close server
                server.quit()
                

    # A convenience function for changing a voter
    @staticmethod
    def change_voter_eligibility(voter_id, eligibility_status_name):
        # Retrieve the voter in question
        voter = Voter.objects.get(user__username=voter_id)

        # Resolve the input
        eligibility_status = True if eligibility_status_name == 'Eligible' else False

        # Modify the field in question with the given value
        voter.eligibility_status = eligibility_status

        # Save changes
        voter.save()

    # A convenience function for deleting a voter
    @staticmethod
    def delete_voter(user_id):
        # Take note that it is not really the voter that is deleted, but the user associated with that voter
        user = User.objects.get(id=user_id)

        # Get rid of that user
        user.delete()

    def display_objects(self, page, query=False):
        # Show everything if the query is empty
        if query is False:
            voters = Voter.objects.all().order_by('user__username')
        else:
            voters = Voter.objects.filter(
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            ) \
                .order_by('user__username')

        colleges = College.objects.all().order_by('name')

        paginator = Paginator(voters, self.objects_per_page)
        paginated_voters = paginator.get_page(page)

        context = {
            'voters': paginated_voters,
            'colleges': colleges,
        }

        return context

    def get(self, request):
        page = request.GET.get('page', False)
        query = request.GET.get('query', False)

        context = self.display_objects(page if page is not False else 1, query)

        return render(request, self.template_name, context)

    def post(self, request):
        form_type = request.POST.get('form-type', False)

        # Only allow editing while there are no elections ongoing and there are no votes in the database
        # if not ResultsView.is_election_ongoing() and ResultsView.is_votes_empty():
        if form_type is not False:
             # The submitted form is for adding a voter
            if form_type == 'add-voter':
                first_name = request.POST.get('voter-firstnames', False)
                last_name = request.POST.get('voter-lastname', False)
                username = request.POST.get('voter-id', False)
                college_name = request.POST.get('voter-college', False)
                voting_status_name = request.POST.get('voter-voting-status', False)
                eligibility_status_name = request.POST.get('voter-eligibility-status', False)

                if first_name is not False and last_name is not False and username is not False \
                        and college_name is not False \
                        and voting_status_name is not False and eligibility_status_name is not False:
                    try:
                        with transaction.atomic():
                            # Create the voter
                            self.create_voter(first_name, last_name, username, college_name, voting_status_name,
                                                eligibility_status_name)

                            # Display a success message
                            messages.success(request, 'Voter successfully created.')
                    except IntegrityError:
                        messages.error(request, 'A voter with that ID number already exists.')
                    except College.DoesNotExist:
                        messages.error(request, 'That college does not exist.')

                    context = self.display_objects(1)

                    return render(request, self.template_name, context)
                else:
                    # If the form type is unknown, it's an invalid request, so stay on the page and then show an error
                    # message
                    messages.error(request, 'Invalid request.')

                    context = self.display_objects(1)

                    return render(request, self.template_name, context)
            elif form_type == 'add-bulk-voter':
                # The submitted form is for adding voters in bulk
                voting_status_name = request.POST.get('voter-voting-status', False)
                eligibility_status_name = request.POST.get('voter-eligibility-status', False)

                if request.FILES['voters-list'] is not None \
                        and voting_status_name is not None \
                        and eligibility_status_name is not None:
                    # Get the file from the request object
                    file = request.FILES['voters-list']

                    # Load all rows from the uploaded file
                    num_voters_added = 0
                    has_passed_header = False

                    # List of all voter information to be added
                    voter_info = []

                    # Either all voters are added, or none at all
                    # Iterate all rows
                    for row in file:
                        # Convert the row to string
                        row_str = row.decode('utf-8').strip()

                        # Skip the first row (the header)
                        if not has_passed_header:
                            has_passed_header = True

                            continue

                        # Check for missing rows
                        try:
                            voter_data_split = row_str.split(',', 4)

                            if len(voter_data_split) != 4:
                                raise ValueError
                        except ValueError:
                            messages.error(request,
                                            'There were missing fields in the uploaded list. No voters were'
                                            ' added.')

                            context = self.display_objects(1)

                            return render(request, self.template_name, context)

                        # Get specific values
                        id_number = voter_data_split[0].strip()
                        last_name = voter_data_split[1].strip()
                        first_names = voter_data_split[2].strip()
                        college = voter_data_split[3].strip()

                        # If the inputs contain invalid data, stop processing immediately
                        if User.objects.filter(username=id_number).count() > 0 \
                                or College.objects.filter(name=college).count() == 0:
                            messages.error(request,
                                            'The uploaded list contained invalid voter data or voters who were already'
                                            ' added previously. No further voters were added. (Error at row ' + repr(
                                                num_voters_added + 2) + ')')

                            context = self.display_objects(1)

                            return render(request, self.template_name, context)

                        # Add them to the list
                        voter_info.append(
                            {
                                'id_number': id_number,
                                'last_name': last_name,
                                'first_names': first_names,
                                'college': college,
                            }
                        )

                        # Increment the added voter count
                        num_voters_added += 1

                    # If the file uploaded was empty
                    if num_voters_added == 0:
                        messages.error(request,
                                        'The uploaded list did not contain any voters.')

                    current_row = 0

                    try:
                        for voter in voter_info:
                            with transaction.atomic():
                                # Try to create the voter
                                self.create_voter(
                                    voter['first_names'],
                                    voter['last_name'],
                                    voter['id_number'],
                                    voter['college'],
                                    voting_status_name,
                                    eligibility_status_name
                                )

                            current_row += 1

                        # Display a success message after all voters have been successfully added
                        messages.success(request, 'All {0} voter(s) successfully added.'.format(num_voters_added))
                    except IntegrityError:
                        messages.error(request, 'A voter with that ID number already exists. (Error at row ' + repr(
                            current_row) + ')')
                    except College.DoesNotExist:
                        messages.error(request,
                                        'The uploaded list contained invalid voter data. No voters were added. '
                                        '(Error at row ' + repr(current_row) + ')')

                    context = self.display_objects(1)

                    return render(request, self.template_name, context)
                else:
                    # If the form type is unknown, it's an invalid request, so stay on the page and then show an error
                    # message
                    messages.error(request, 'Invalid request.')

                    context = self.display_objects(1)

                    return render(request, self.template_name, context)
            if (not ResultsView.get_election_state() or ResultsView.get_election_state() == ElectionState.ARCHIVED.value) and ResultsView.is_votes_empty():
                if form_type == 'edit-voter':
                    # The submitted form is for editing a voter
                    page = request.POST.get('page', False)
                    voter_id = request.POST.get('edit-id', False)
                    eligibility_status_name = request.POST.get('voter-eligibility-status', False)

                    if page is not False and voter_id is not False and eligibility_status_name is not False:
                        try:
                            with transaction.atomic():
                                # Edit the voter
                                self.change_voter_eligibility(voter_id, eligibility_status_name)

                                # Display a success message
                                messages.success(request, 'Voter successfully edited.')
                        except Voter.DoesNotExist:
                            messages.error(request, 'No such voter exists.')

                        context = self.display_objects(page)

                        return render(request, self.template_name, context)
                    else:
                        # If the form type is unknown, it's an invalid request, so stay on the page and then show an error
                        # message
                        messages.error(request, 'Invalid request.')

                        context = self.display_objects(1)

                        return render(request, self.template_name, context)
                elif form_type == 'delete-voter':
                    # The submitted form is for deleting voters
                    voters_list = request.POST.getlist('voters')

                    if voters_list is not False and len(voters_list) > 0:
                        election_state = ResultsView.get_election_state()

                        if (election_state == ElectionState.ONGOING.value or election_state == ElectionState.PAUSED.value):
                            messages.error(request,
                                                'Cannot delete voters while an election is ongoing')
                        else:
                            try:
                                voters_deleted = 0

                                # Try to delete each voter in the list
                                with transaction.atomic():
                                    for voter in voters_list:
                                        self.delete_voter(voter)

                                        voters_deleted += 1

                                    messages.success(request,
                                                        "All {0} voter(s) successfully deleted.".format(voters_deleted))
                            except User.DoesNotExist:
                                # If the user does not exist
                                messages.error(request,
                                                'One of the selected users has not existed in the first place. '
                                                'No voters were deleted.')

                        context = self.display_objects(1)

                        return render(request, self.template_name, context)
                    else:
                        # If the form type is unknown, it's an invalid request, so stay on the page and then show an error
                        # message
                        messages.error(request, 'Invalid request.')

                        context = self.display_objects(1)

                        return render(request, self.template_name, context)
                else:
                    # If the form type is unknown, it's an invalid request, so stay on the page and then show an error
                    # message
                    messages.error(request, 'Invalid request.')

                    context = self.display_objects(1)

                    return render(request, self.template_name, context)
            else:
                # If the form type is unknown, it's an invalid request, so stay on the page and then show an error
                # message
                messages.error(request, 'You cannot do that now because there are still votes being tracked. There may be '
                                    'elections still ongoing, or you haven\'t archived the votes yet.')

                context = self.display_objects(1)

                return render(request, self.template_name, context)
        else:
            # If no objects are received, it's an invalid request, so stay on the page and then show an error
            # message
            messages.error(request, 'Invalid request.')

            context = self.display_objects(1)

            return render(request, self.template_name, context)
        # else:
        #     messages.error(request, 'You cannot do that now because there are still votes being tracked. There may be '
        #                             'elections still ongoing, or you haven\'t archived the votes yet.')

        #     context = self.display_objects(1)

        #     return render(request, self.template_name, context)


class CandidatesView(OfficerView):
    template_name = 'officer/officer-candidate.html'

    def display_objects(self, page, query=False):
        # Show everything if the query is empty
        if query is False:
            candidates = Candidate.objects.all().order_by('voter__user__username')
        else:
            candidates = Candidate.objects.filter(
                Q(voter__user__username__icontains=query) |
                Q(voter__user__first_name__icontains=query) |
                Q(voter__user__last_name__icontains=query) |
                Q(position__base_position__name__icontains=query) |
                Q(position__unit__name=query) |
                Q(party__name__icontains=query)
            ) \
                .order_by('voter__user__username')

        paginator = Paginator(candidates, self.objects_per_page)
        paginated_candidates = paginator.get_page(page)

        context = {
            'candidates': paginated_candidates,
        }

        return context

    def get(self, request):
        page = request.GET.get('page', False)
        query = request.GET.get('query', False)

        context = self.display_objects(page if page is not False else 1, query)

        return render(request, self.template_name, context)

    def post(self, request):
        self.get(request)


class ResultsView(OfficerView):
    template_name = 'officer/officer-results.html'

    def display_objects(self, page, query=False, pollquery=False):
        # Retrieve all colleges
        colleges = College.objects.all().order_by('name')

        # Set a flag indicating whether elections have started or not
        election_state = self.get_election_state()

        # Show the checkbox page when the elections aren't on
        if election_state == ElectionState.FINISHED.value:
            # Get all batches from the batch of the current year until the batch of the year six years from the current
            # year
            current_year = datetime.datetime.now().year

            batches = ['1' + str(year)[2:] for year in range(current_year, current_year - 6, -1)]
            batches[-1] = batches[-1] + ' and below'

            # Retrieve all positions
            positions = Position.objects.all().order_by('base_position__name', 'unit__college__name', 'unit__name')

            polls = Poll.objects.all().order_by('name')

            # QUERY FOR TOTAL VOTE
            TOTAL_STUDENTS = ("""
                WITH population AS (
                    SELECT
                        vv.campus_id    AS campus,
                        vv.college_id   AS college,
                        vv.batch        AS batch,
                        COUNT(vv.id)    AS population
                    FROM
                        vote_voter vv
                    GROUP BY ROLLUP (
                        vv.campus_id,
                        vv.college_id,
                        vv.batch
                    )
                    ORDER BY
                        vv.campus_id,
                        vv.college_id,
                        vv.batch
                ),
                population_name AS (
                    SELECT
                        vc.name         AS campus,
                        vco.name        AS college,
                        p.batch         AS batch,
                        p.population    AS population
                    FROM
                        population p
                            LEFT JOIN
                                vote_campus vc
                            ON
                                vc.id=p.campus
                            LEFT JOIN
                                vote_college vco
                            ON
                                vco.id=p.college
                )
                SELECT  *
                FROM    population_name;
            """)

            total_student = 0

            with connection.cursor() as cursor:
                cursor.execute(TOTAL_STUDENTS)

                total_student = cursor.fetchall()[-1][-1]

            if query is not False:
                # Count the votes of all candidates by position
                TOTAL_VOTES_QUERY = ("""
                    WITH all_candidates AS (
                    	SELECT
                    		c.id AS candidate_id,
                    		c.position_id AS position_id,
                    		COALESCE(vs.position_id, NULL)  AS has_been_voted
                    	FROM
                    		vote_candidate c
                    	LEFT JOIN
                    		vote_voteset vs                 ON c.id = vs.candidate_id
                    	UNION ALL
                    	SELECT
                    		vs.candidate_id                 AS candidate_id,
                    		vs.position_id                  AS position_id,
                    		COALESCE(vs.position_id, NULL)  AS has_been_voted
                    	FROM
                    		vote_voteset vs
                    	WHERE
                    		vs.candidate_id IS NULL
                    ),
                    raw_count_position AS (
                    	SELECT
                    		bp.name                     AS position,
                    		u.name                      AS unit,
                    		ac.candidate_id             AS candidate_id,
                    		COUNT(ac.has_been_voted)    AS votes
                    	FROM
                    		all_candidates ac
                    	LEFT JOIN
                    		vote_position p ON ac.position_id = p.id
                    	LEFT JOIN
                    		vote_baseposition bp ON p.base_position_id = bp.id
                    	LEFT JOIN
                    		vote_unit u ON p.unit_id = u.id
                    	WHERE
                    		p.identifier = %s
                    	GROUP BY
                    		bp.name, u.name, ac.position_id, ac.candidate_id
                    ),
                    candidate_name AS (
                    	SELECT
                    		rcp.position,
                    		rcp.unit,
                    		COALESCE(u.first_name || ' ' || u.last_name, '(abstained)') AS candidate,
                    		p.name AS party,
                    		rcp.votes
                    	FROM
                    		raw_count_position rcp
                    	LEFT JOIN
                    		vote_candidate c ON rcp.candidate_id = c.id
                    	LEFT JOIN
                    		vote_voter v ON c.voter_id = v.id
                    	LEFT JOIN
                    		auth_user u ON v.user_id = u.id
                    	LEFT JOIN
                    		vote_party p ON c.party_id = p.id
                    ),
                    party_name AS (
                    	SELECT
                    		cn.position AS position,
                    		cn.unit AS unit,
                    		cn.candidate AS candidate,
                    		CASE cn.candidate
                    			WHEN '(abstained)' THEN '(abstained)'
                    			ELSE COALESCE(cn.party, 'Independent')
                    		END AS party,
                    		cn.votes AS votes
                    	FROM
                    		candidate_name cn
                    ),
                    vote_position AS (
                        SELECT
                            pn2.position    AS position,
                            pn2.unit        AS unit,
                            SUM(pn2.votes)  AS votes
                        FROM 
                            party_name pn2
                        GROUP BY
                            pn2.position,
                            pn2.unit
                    ),
                    -- Gets the whole population based by campus, college, batch
                    population AS (
                        SELECT
                            vv.campus_id    AS campus_id,
                            vv.college_id   AS college_id,
                            vv.batch        AS batch,
                            COUNT(vv.id)    AS population
                        FROM
                            vote_voter vv
                        GROUP BY ROLLUP (
                            vv.campus_id,
                            vv.college_id,
                            vv.batch
                        )
                        ORDER BY
                            vv.campus_id,
                            vv.college_id,
                            vv.batch
                    ),
                    -- Gets all the unit_population
                    unit_population AS (
                        SELECT
                            vu.name         AS name,
                            p.population    AS population
                        FROM
                            vote_unit vu
                        JOIN
                            party_name pn ON
                                pn.unit = vu.name
                        LEFT JOIN
                            population p ON
                                COALESCE(p.campus_id, -1) = COALESCE(vu.campus_id, -1) AND
                                COALESCE(p.college_id, -1) = COALESCE(vu.college_id, -1) AND
                                (
                                    p.batch = vu.batch OR
                                    p.batch IS NULL AND vu.college_id IS NULL
                                )
                    ),
                    -- Sum of total voters
                    total_voters AS (
                        SELECT
                            SUM(pn.votes)   AS total
                        FROM
                            party_name      pn
                    )
                    SELECT  *
                    FROM    (
                        (
                            SELECT
                                pn.position     AS position,
                                pn.unit         AS unit,
                                pn.candidate    AS candidate,
                                pn.party        AS party,
                                pn.votes        AS votes
                            FROM
                                party_name pn
                        ) UNION (
                            SELECT
                                NULL                        AS position,
                                up.name                     AS unit,
                                NULL                        AS candidate,
                                NULL                        AS party,
                                up.population - tv.total    AS votes
                            FROM
                                unit_population up
                            JOIN
                                total_voters tv ON true
                        )
                    ) final
                    ORDER BY
                        votes DESC,
                        candidate;
                """)

                # Correctly format the query
                query_formatted = query.replace('-', '')

                vote_results = {}

                with connection.cursor() as cursor:
                    cursor.execute(TOTAL_VOTES_QUERY, [ query_formatted ])

                    vote_results[query] = cursor.fetchall()

                # Create a shorter JSON version of the results
                vote_results_json = {}

                for result in vote_results[query]:
                    # print(result)

                    if result[4] != None:
                        vote_results_json[str(result[2])] = int(result[4])

                vote_results_json = json.dumps(vote_results_json)

            elif pollquery is not False:
                # Count the votes of all candidates by position
                TOTAL_POLL_VOTES_QUERY = ("""
                    SELECT
                        p.name AS poll_question,
                        SUM(
                            CASE
                                WHEN ps.answer = 'yes' AND p.identifier = %s THEN 1
                                ELSE 0
                            END
                        ) AS answered_yes,
                        SUM(
                            CASE
                                WHEN ps.answer = 'no' AND p.identifier = %s THEN 1
                                ELSE 0 END
                            ) AS answered_no
                    FROM
                        vote_pollset ps
                    LEFT JOIN
                        vote_poll p
                    ON
                        ps.poll_id = p.id
                    AND
                        p.identifier = %s
                    GROUP BY
                        p.name;
                """)

                # Correctly format the query
                poll_query_formatted = pollquery.replace('-', '')

                poll_results = {}

                with connection.cursor() as cursor:
                    cursor.execute(TOTAL_POLL_VOTES_QUERY, [poll_query_formatted, poll_query_formatted, poll_query_formatted])

                    poll_results[pollquery] = cursor.fetchall()

                # Create a shorter JSON version of the results
                poll_results_json = {}

                for result in poll_results[pollquery]:
                    # print(result)

                    poll_results_json[result[0]] = (result[1], result[2])

                poll_results_json = json.dumps(poll_results_json)

            context = {
                'election_state': election_state,
                'colleges': colleges,
                'batches': batches,
                'positions': positions,
                'polls': polls,
                'poll_results': poll_results if pollquery is not False else False,
                'poll_results_json': poll_results_json if pollquery is not False else False,
                'poll_identifier': pollquery,
                'vote_results': vote_results if query is not False else False,
                'vote_results_json': vote_results_json if query is not False else False,
                'identifier': query,
                'total_student': total_student
            }
        else:
            # Show the eligible batches when the elections are on
            college_batch_dict = {}

            college_batches = ElectionStatus.objects.all().order_by('college__name', '-batch')

            for college_batch in college_batches:
                if college_batch.college.name not in college_batch_dict.keys():
                    college_batch_dict[college_batch.college.name] = []

                college_batch_dict[college_batch.college.name].append(college_batch.batch)

            # As well as the the relevant data from the election
            votes = Vote.objects.all()

            # Overall votes
            overall_votes = votes.count()

            # Total registered voters
            overall_registered_voters = Voter.objects.count()
            
            # Voter turnout
            overall_turnout = overall_votes / overall_registered_voters * 100 if overall_registered_voters != 0 else 0

            # Votes today
            now = datetime.datetime.now()

            votes_today = votes.filter(timestamp__day=now.day)

            overall_votes_today = votes_today.count()

            reference_12 = now.replace(hour=12, minute=0, second=0, microsecond=0)
            reference_15 = now.replace(hour=15, minute=0, second=0, microsecond=0)
            reference_18 = now.replace(hour=18, minute=0, second=0, microsecond=0)

            votes_today_12 = votes_today.filter(timestamp__lte=reference_12).count()
            votes_today_15 = votes_today.filter(timestamp__lte=reference_15).count()
            votes_today_18 = votes_today.filter(timestamp__lte=reference_18).count()

            # Votes overall per day per batch
            BATCH_QUERY = ("""
                WITH votes_12 AS (
                	SELECT
                		DATE(v12.timestamp)         AS date12,
                		v12.voter_batch             AS batch12,
                		COUNT(v12.serial_number)    AS count12
                	FROM
                		vote_vote v12
                	WHERE
                		v12.timestamp <= DATE(v12.timestamp) + interval '12 hours'
                	GROUP BY
                		v12.timestamp,
                		v12.voter_batch
                ),
                votes_15 AS (
                	SELECT
                		DATE(v15.timestamp)         AS date15,
                		v15.voter_batch             AS batch15,
                		COUNT(v15.serial_number)    AS count15
                	FROM
                		vote_vote v15
                	WHERE
                		v15.timestamp <= DATE(v15.timestamp) + interval '15 hours'
                	GROUP BY
                		DATE(v15.timestamp),
                		v15.voter_batch
                ),
                votes_18 AS (
                	SELECT
                		DATE(v18.timestamp)         AS date18,
                		v18.voter_batch             AS batch18,
                		COUNT(v18.serial_number)    AS count18
                	FROM
                		vote_vote v18
                	WHERE
                		v18.timestamp <= DATE(v18.timestamp) + interval '18 hours'
                	GROUP BY
                		DATE(v18.timestamp),
                		v18.voter_batch
                )
                SELECT
                	DATE(v.timestamp)               AS date,
                	v.voter_batch                   AS batch,
                	COUNT(v.serial_number)          AS total_count,
                	COALESCE(votes_12.count12, 0)   AS as_of_12_nn,
                	COALESCE(votes_15.count15, 0)   AS as_of_3_pm,
                	COALESCE(votes_18.count18, 0)   AS as_of_6_pm
                FROM
                	vote_vote v
                LEFT JOIN
                	votes_12 ON
                		DATE(v.timestamp) = votes_12.date12
                		AND v.voter_batch = votes_12.batch12
                LEFT JOIN
                	votes_15 ON
                		DATE(v.timestamp) = votes_15.date15
                		AND v.voter_batch = votes_15.batch15
                LEFT JOIN
                	votes_18 ON
                		DATE(v.timestamp) = votes_18.date18
                		AND v.voter_batch = votes_18.batch18
                GROUP BY
                	DATE(v.timestamp),
                	v.voter_batch,
                    votes_12.count12,
                    votes_15.count15,
                    votes_18.count18
                ORDER BY
                   DATE(v.timestamp) DESC,
                   v.voter_batch ASC;
            """)

            batch_results = []

            with connection.cursor() as cursor:
                cursor.execute(BATCH_QUERY)

                batch_results.append(cursor.fetchall())

            # print(batch_results)

            # Get the eligible colleges
            eligible_colleges = ElectionStatus.objects.values('college').distinct()
            eligible_colleges = [College.objects.get(id=eligible_college['college']) for eligible_college in eligible_colleges]

            overall_votes_college = {}

            for eligible_college in eligible_colleges:
                overall_votes_college[eligible_college.name] = Vote.objects.filter(
                    voter_college=eligible_college.id).count()

            # Votes per day per college per batch
            COLLEGE_BATCH_QUERY = ("""
                WITH votes_12 AS (
                	SELECT
                		DATE(v12.timestamp)         AS date12,
                		v12.voter_batch             AS batch12,
                		COUNT(v12.serial_number)    AS count12
                	FROM
                		vote_vote v12
                	WHERE
                		v12.timestamp <= DATE(v12.timestamp) + interval '12 hours'
                		AND v12.voter_college_id = %s
                	GROUP BY
                		DATE(v12.timestamp),
                		v12.voter_batch
                ),
                votes_15 AS (
                	SELECT
                		DATE(v15.timestamp)         AS date15,
                		v15.voter_batch             AS batch15,
                		COUNT(v15.serial_number)    AS count15
                	FROM
                		vote_vote v15
                	WHERE
                		v15.timestamp <= DATE(v15.timestamp) + interval '15 hours'
                		AND v15.voter_college_id = %s
                	GROUP BY
                		DATE(v15.timestamp),
                		v15.voter_batch
                ),
                votes_18 AS (
                	SELECT
                		DATE(v18.timestamp)         AS date18,
                		v18.voter_batch             AS batch18,
                		COUNT(v18.serial_number)    AS count18
                	FROM
                		vote_vote v18
                	WHERE
                		v18.timestamp <= DATE(v18.timestamp) + interval '18 hours'
                		AND v18.voter_college_id = %s
                	GROUP BY
                		DATE(v18.timestamp),
                		v18.voter_batch
                )
                SELECT
                	DATE(v.timestamp)               AS date,
                	v.voter_batch                   AS batch,
                	COUNT(v.serial_number)          AS total_count,
                	COALESCE(votes_12.count12, 0)   AS as_of_12_nn,
                	COALESCE(votes_15.count15, 0)   AS as_of_3_pm,
                	COALESCE(votes_18.count18, 0)   AS as_of_6_pm
                FROM
                	vote_vote v
                LEFT JOIN
                	votes_12 ON
                		DATE(v.timestamp) = votes_12.date12
                		AND v.voter_batch = votes_12.batch12
                LEFT JOIN
                	votes_15 ON
                		DATE(v.timestamp) = votes_15.date15
                		AND v.voter_batch = votes_15.batch15
                LEFT JOIN
                	votes_18 ON
                		DATE(v.timestamp) = votes_18.date18
                		AND v.voter_batch = votes_18.batch18
                WHERE
                	v.voter_college_id = %s
                GROUP BY
                	DATE(v.timestamp),
                	v.voter_batch,
                    votes_12.count12,
                    votes_15.count15,
                    votes_18.count18
                ORDER BY
                   DATE(v.timestamp) DESC,
                   v.voter_batch ASC;
            """)

            college_batch_results = {}

            for eligible_college in eligible_colleges:
                with connection.cursor() as cursor:
                    col_id = eligible_college.id
                    cursor.execute(
                        COLLEGE_BATCH_QUERY,
                        [ col_id, col_id, col_id, col_id ]
                    )

                    college_batch_results[eligible_college.name] = cursor.fetchall()

            context = {
                'election_state': election_state,
                'colleges': colleges,
                'college_batch_dict': college_batch_dict,
                'overall_votes': overall_votes,
                'overall_registered_voters': overall_registered_voters,
                'overall_turnout': overall_turnout,
                'overall_votes_today': overall_votes_today,
                'votes_today_12': votes_today_12,
                'votes_today_15': votes_today_15,
                'votes_today_18': votes_today_18,
                'batch_results': batch_results,
                'eligible_colleges': eligible_colleges,
                'overall_votes_college': overall_votes_college,
                'college_batch_results': college_batch_results,
            }

        return context

    # @staticmethod
    # def is_election_ongoing():
    #     return ElectionStatus.objects.all().exists()

    @staticmethod
    def get_election_state():
        try:
            return Election.objects.latest('timestamp').state
        except:
            return None

    @staticmethod
    def is_votes_empty():
        return not Vote.objects.all().exists()

    # Generate a random passcode for a user
    @staticmethod
    def generate_passcode():
        # Length of the passcode
        length = 8

        # The character domain of the passcode
        charset = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789'

        # The passcode to be generated
        passcode = ''

        # Generate a random passcode of specified length
        for index in range(length):
            passcode += charset[randint(0, len(charset) - 1)]

        return passcode

    def get(self, request):
        page = request.GET.get('page', False)
        query = request.GET.get('query', False)
        pollquery = request.GET.get('pollquery', False)

        context = self.display_objects(page if page is not False else 1, query, pollquery)

        return render(request, self.template_name, context)

    def post(self, request):
        form_type = request.POST.get('form-type', False)

        if form_type is not False:
            # The submitted form is for starting the elections
            """
            Can't be used in an online setting
            if form_type == 'start-elections':
                # If the elections have already started, it can't be started again!
                if self.is_election_ongoing():
                    messages.error(request, 'The elections have already been started.')
                elif not self.is_votes_empty():
                    # If there still are votes left from the previous elections, the elections can't be started yet
                    messages.error(request,
                                   'The votes from the previous election haven\'t been archived yet. Archive them '
                                   'first before starting this election.')
                else:
                    # Only continue if the re-authentication password indeed matches the password of the current
                    # COMELEC officer
                    reauth_password = request.POST.get('reauth', False)

                    if reauth_password is False \
                            or authenticate(username=request.user.username, password=reauth_password) is None:
                        messages.error(request,
                                       'The elections weren\'t started because the password was incorrect. Try again.')
                    else:
                        college_batches = {}

                        # Collect all batches per college
                        for college in College.objects.all().order_by('name'):
                            college_batches[college.name] = request.POST.getlist(college.name + '-batch')

                        # Keep track of whether no checkboxes where checked
                        empty = True

                        # List of all voters
                        voters = [ ]

                        # Add each into the database
                        for college, batches in college_batches.items():
                            # Get the college object from the name
                            try:
                                college_object = College.objects.get(name=college)

                                # Then use that object to create the an election status value for these specific batches
                                for batch in batches:
                                    empty = False

                                    ElectionStatus.objects.create(college=college_object, batch=batch)
                                    batch_voters = list(
                                        Voter.objects.filter(
                                            college=college_object,
                                            user__username__startswith=str(batch),
                                            voting_status=False,
                                            eligibility_status=True
                                        ).values('user__username')
                                    )

                                    # print(batch_voters)
                                    voters += batch_voters
                            except College.DoesNotExist:
                                # If the college does not exist
                                messages.error(request, 'Internal server error.')

                        # Check whether batches were actually selected in the first place
                        if not empty:
                            for index, voter in enumerate(voters):
                                send_email(voter['user__username'])
                                print('Email sent to ' + voter['user__username'] + '.' + str(index) + ' out of ' + str(len(voters)) + ' sent.')

                            messages.success(request, 'The elections have now started.')
                        else:
                            messages.error(request,
                                           'The elections weren\'t started because there were no batches selected at'
                                           ' all.')

                context = self.display_objects(1)

                return render(request, self.template_name, context)
            elif form_type == 'end-elections':
                # If the elections have already ended, it can't be ended again!
                if self.is_election_ongoing():
                    # Only continue if the re-authentication password indeed matches the password of the current
                    # COMELEC officer
                    reauth_password = request.POST.get('reauth', False)

                    if reauth_password is False \
                            or authenticate(username=request.user.username, password=reauth_password) is None:
                        messages.error(request,
                                       'The elections weren\'t ended because the password was incorrect. Try again.')
                    else:
                        # Clear the entire election status table
                        ElectionStatus.objects.all().delete()

                        messages.success(request, 'The elections have now ended.')
                else:
                    messages.error(request, 'The elections have already been ended.')

                context = self.display_objects(1)

                return render(request, self.template_name, context)
            
            if form_type == 'archive':
                # If there are elections ongoing, no archiving may be done yet
                if self.is_election_ongoing():
                    messages.error(request, 'You may not archive while the elections are ongoing.')

                    context = self.display_objects(1)

                    return render(request, self.template_name, context)
                elif self.is_votes_empty():
                    # If there no votes to archive, what's the point?
                    messages.error(request,
                                   'There aren\'t any election results to archive yet.')

                    context = self.display_objects(1)

                    return render(request, self.template_name, context)
                else:
                    # The submitted form is for archiving the election results
                    # Only continue if the re-authentication password indeed matches the password of the current
                    # COMELEC officer
                    reauth_password = request.POST.get('reauth-archive', False)

                    if reauth_password is False \
                            or authenticate(username=request.user.username, password=reauth_password) is None:
                        messages.error(request,
                                       'The election results weren\'t archived because the password was incorrect. '
                                       'Try again.')

                        context = self.display_objects(1)

                        return render(request, self.template_name, context)
                    else:
                        with transaction.atomic():
                            # Count the votes of all candidates
                            TOTAL_VOTES_QUERY = (
                                "WITH all_candidates AS (\n"
                                "	SELECT\n"
                                "		c.id AS 'CandidateID',\n"
                                "		c.position_id AS 'PositionID',\n"
                                "		IFNULL(vs.position_id, NULL) AS 'HasBeenVoted'\n"
                                "	FROM\n"
                                "		vote_candidate c\n"
                                "	LEFT JOIN\n"
                                "		vote_voteset vs ON c.id = vs.candidate_id\n"
                                "	UNION ALL\n"
                                "	SELECT\n"
                                "		vs.candidate_id AS 'CandidateID',\n"
                                "		vs.position_id AS 'PositionID',\n"
                                "		IFNULL(vs.position_id, NULL) AS 'HasBeenVoted'\n"
                                "	FROM\n"
                                "		vote_voteset vs\n"
                                "	WHERE\n"
                                "		vs.candidate_id IS NULL\n"
                                "),\n"
                                "raw_count_position AS (\n"
                                "	SELECT\n"
                                "		bp.name AS 'Position',\n"
                                "		u.name AS 'Unit',\n"
                                "		ac.'CandidateID' AS 'CandidateID',\n"
                                "		COUNT(ac.'HasBeenVoted') AS 'Votes'\n"
                                "	FROM\n"
                                "		all_candidates ac\n"
                                "	LEFT JOIN\n"
                                "		vote_position p ON ac.'PositionID' = p.id\n"
                                "	LEFT JOIN\n"
                                "		vote_baseposition bp ON p.base_position_id = bp.id\n"
                                "	LEFT JOIN\n"
                                "		vote_unit u ON p.unit_id = u.id\n"
                                "	GROUP BY\n"
                                "		ac.'PositionID', ac.'CandidateID'\n"
                                "),\n"
                                "candidate_name AS (\n"
                                "	SELECT\n"
                                "		rcp.'Position',\n"
                                "		rcp.'Unit',\n"
                                "		IFNULL(u.first_name || ' ' || u.last_name, '(abstained)') AS 'Candidate',\n"
                                "		p.name AS 'Party',\n"
                                "		rcp.'Votes'\n"
                                "	FROM\n"
                                "		raw_count_position rcp\n"
                                "	LEFT JOIN\n"
                                "		vote_candidate c ON rcp.'CandidateID' = c.id\n"
                                "	LEFT JOIN\n"
                                "		vote_voter v ON c.voter_id = v.id\n"
                                "	LEFT JOIN\n"
                                "		auth_user u ON v.user_id = u.id\n"
                                "	LEFT JOIN\n"
                                "		vote_party p ON c.party_id = p.id\n"
                                "),\n"
                                "party_name AS (\n"
                                "	SELECT\n"
                                "		cn.'Position' AS 'Position',\n"
                                "		cn.'Unit' AS 'Unit',\n"
                                "		cn.'Candidate' AS 'Candidate',\n"
                                "		CASE cn.'Candidate'\n"
                                "			WHEN '(abstained)' THEN '(abstained)'\n"
                                "			ELSE IFNULL(cn.'Party', 'Independent')\n"
                                "		END AS 'Party',\n"
                                "		cn.'Votes' AS 'Votes'\n"
                                "	FROM\n"
                                "		candidate_name cn\n"
                                ")\n"
                                "SELECT\n"
                                "	pn.'Position' AS 'Position',\n"
                                "	pn.'Unit' AS 'Unit',\n"
                                "	pn.'Candidate' AS 'Candidate',\n"
                                "	pn.'Party' AS 'Party',\n"
                                "	pn.'Votes' AS 'Votes'\n"
                                "FROM\n"
                                "	party_name pn\n"
                                "ORDER BY\n"
                                "	pn.'Position',\n"
                                "	pn.'Unit',\n"
                                "	pn.'Votes' DESC,\n"
                                "	pn.'Candidate';\n"
                            )

                            TOTAL_POLL_VOTES_QUERY = (
                                "SELECT\n"
                                "   p.'name' AS 'Question',\n"
                                "   SUM((CASE WHEN ps.'answer' = 'yes' THEN 1 ELSE 0 END)) AS 'Yes',\n"
                                "   SUM((CASE WHEN ps.'answer' = 'no' THEN 1 ELSE 0 END)) AS 'No'\n"
                                "FROM\n"
                                "   vote_pollset ps\n"
                                "LEFT JOIN\n"
                                "   vote_poll p\n"
                                "ON\n"
                                "   ps.'poll_id' = p.'id'\n"
                                "GROUP BY\n"
                                "   p.'id';\n"
                            )

                            vote_results = {}
                            poll_results = {}

                            with connection.cursor() as cursor:
                                cursor.execute(TOTAL_VOTES_QUERY, [])

                                columns = [col[0] for col in cursor.description]
                                vote_results['results'] = cursor.fetchall()

                            with connection.cursor() as cursor:
                                cursor.execute(TOTAL_POLL_VOTES_QUERY, [])

                                poll_columns = [col[0] for col in cursor.description]
                                poll_results['results'] = cursor.fetchall()

                            # Create a response object, and classify it as a CSV response
                            response = HttpResponse(content_type='text/csv')
                            response['Content-Disposition'] = 'attachment; filename="results.csv"'

                            # Then write the results to a CSV file
                            writer = csv.writer(response)

                            writer.writerow(["Election Results"])

                            writer.writerow(columns)

                            for row in vote_results['results']:
                                writer.writerow(list(row))

                            writer.writerow("")

                            writer.writerow(["Poll Results"])

                            writer.writerow(poll_columns)

                            for row in poll_results['results']:
                                writer.writerow(list(row))

                            # Clear all users who are voters
                            # This also clears the following tables: voters, candidates, takes, vote set, poll set
                            User.objects.filter(groups__name='voter').delete()

                            # Clear all issues
                            Issue.objects.all().delete()

                            # Clear all votes
                            Vote.objects.all().delete()

                            # Clear all polls
                            Poll.objects.all().delete()

                            # Clear all batch positions
                            Position.objects.filter(base_position__type=BasePosition.BATCH).delete()

                            # Clear all batch units
                            Unit.objects.filter(college__isnull=False, batch__isnull=False)

                            # Show a Save As box so the user may download it
                            return response
            else:
                # If the form type is unknown, it's an invalid request, so stay on the page and then show an error
                # message
                messages.error(request, 'Invalid request.')

                context = self.display_objects(1)

                return render(request, self.template_name, context)
            """
        else:
            # If no objects are received, it's an invalid request, so stay on the page and then show an error
            # message
            messages.error(request, 'Invalid request.')

            context = self.display_objects(1)

            return render(request, self.template_name, context)


class PasscodeView(UserPassesTestMixin, View):
    template_name = 'officer/password_generator.html'

    # Check whether the user id of the queried user is currently in
    @staticmethod
    def is_currently_in(user_id):
        # Query all non-expired sessions
        # use timezone.now() instead of datetime.now() in latest versions of Django
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        uid_list = []

        # Build a list of user ids from that query
        for session in sessions:
            data = session.get_decoded()
            uid_list.append(data.get('_auth_user_id', None))

        print(User.objects.filter(id__in=uid_list))

        # Query all logged in users based on id list
        return User.objects.filter(id=user_id, id__in=uid_list).count() > 0

    # Generate a random passcode for a user
    @staticmethod
    def generate_passcode():
        # Length of the passcode
        length = 8

        # The character domain of the passcode
        charset = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789'

        # The passcode to be generated
        passcode = ''

        # Generate a random passcode of specified length
        for index in range(length):
            passcode += charset[randint(0, len(charset) - 1)]

        return passcode

    @staticmethod
    def is_eligible(voter):
        status = ElectionStatus.objects.filter(college__name=voter.college.name)
        batch = voter.batch
        flag = False

        for s in status:
            if batch == s.batch:
                flag = True
                break
            if "and below" in s.batch and int(batch) <= int(s.batch[:3]):
                flag = True
                break

        return voter.eligibility_status and flag

    # Check whether the user accessing this page is a COMELEC officer or not
    def test_func(self):
        try:
            return Group.objects.get(name='comelec') in self.request.user.groups.all()
        except Group.DoesNotExist:
            return False

    def get(self, request):
        # Get this page
        context = {'message': ''}

        return render(request, self.template_name, context)

    def post(self, request):
        # Set error messages up
        DOES_NOT_EXIST = 'DNE'
        ALREADY_IN = 'AI'
        ALREADY_VOTED = 'AV'
        INELIGIBLE = 'IE'
        INVALID_REQUEST = 'IR'

        # Please note that the user's password really isn't returned here (that would be indicative of poor security)
        # What these lines actually do is generate a new password every time a valid user is queried
        # Then the user's password is actually changed to this new password
        # There are two reasons for this:
        #  1) To be able to actually show something to the user, because passwords can't be shown from the DB,
        #  2) A different passcode is given every time a user asks for a passcode, for security purposes.

        # Get the ID number queried
        id_number = request.POST.get('id-number', False)

        # If there was no ID number sent, return an invalid request error
        if id_number is not False:
            # Check whether a user with the queried ID number exists
            try:
                # Get the user and voter associated with that ID number
                id_number = id_number.strip()

                user = User.objects.get(username=id_number)
                voter = Voter.objects.get(user__username=id_number)

                # Check if that user is eligible at all
                if self.is_eligible(voter):
                    # Check if that user has already voted
                    if not voter.voting_status:
                        # Check if that user is currently logged in
                        if not self.is_currently_in(user.id):
                            # Generate a passcode
                            passcode = self.generate_passcode()

                            # And then change the queried user's password to the generated passcode
                            user.set_password(passcode)

                            # Save the changes to the user
                            user.save()

                            # Store that passcode in the context
                            context = {'message': passcode}
                        else:
                            # If not, we can't modify a currently logged in user's password, so return an already in error
                            # Also, this would be a red flag, because this means someone has entered an ID number of someone
                            # currently in the process of voting
                            context = {'message': ALREADY_IN}
                    else:
                        # If the voter has already voted, the passcode can't be changed for that voter anymore
                        context = {'message': ALREADY_VOTED}
                else:
                    # If the voter is not eligible (or the voter's college is not eligible), don't churn out a passcode
                    context = {'message': INELIGIBLE}
            except (User.DoesNotExist, Voter.DoesNotExist):
                # That user does not exist, so return a does not exist error.
                context = {'message': DOES_NOT_EXIST}
        else:
            # Send back an invalid request error.
            context = {'message': INVALID_REQUEST}

        # Go back to this page
        return render(request, self.template_name, context)


@user_passes_test(officer_test_func)
def json_details(request, voter_id):
    # Get the voter
    try:
        voter = Voter.objects.get(user__username=voter_id)
    except Voter.DoesNotExist:
        return JsonResponse({'response': "(This voter does not exist)"})

    print({'first_names': voter.user.first_name, 'last_name': voter.user.last_name,
           'id_number': voter.user.username, 'college': voter.college.name,
           'voting_status': voter.voting_status, 'eligibility_status': voter.eligibility_status})

    # Then return its details
    return JsonResponse({'first_names': voter.user.first_name, 'last_name': voter.user.last_name,
                         'id_number': voter.user.username, 'college': voter.college.name,
                         'voting_status': voter.voting_status, 'eligibility_status': voter.eligibility_status})
