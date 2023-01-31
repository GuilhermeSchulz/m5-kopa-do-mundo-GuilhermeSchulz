from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Team
from django.forms.models import model_to_dict
import datetime


class NegativeTitlesError(Exception):
    def __init__(self, message):
        self.message = message


def validate_titles(titles):
    if titles < 0:
        raise NegativeTitlesError("titles cannot be negative")


class InvalidYearCupError(Exception):
    def __init__(self, message):
        self.message = message


def validate_first_cup(first_cup):
    date = datetime.datetime.strptime(first_cup, "%Y-%m-%d")
    first = datetime.datetime(1930, 1, 1)
    cup_years = first.year
    curr = datetime.datetime.now()
    curr_year = curr.year * 1
    cup = False
    if date.year * 1 < first.year * 1:
        raise InvalidYearCupError("there was no world cup this year")
    while cup_years * 1 < curr_year:
        if (date.year * 1) != cup_years:
            cup = False
        elif date.year * 1 == cup_years:
            cup = True
        if cup is True:
            break
        cup_years += 4
    if cup is False:
        raise InvalidYearCupError("there was no world cup this year")


class ImpossibleTitlesError(Exception):
    def __init__(self, message):
        self.message = message


def validate_titles_years(titles, first_cup):
    date_now = datetime.datetime.now()
    first_cup = datetime.datetime.strptime(first_cup, "%Y-%m-%d")
    first_cup_year = first_cup.year * 1
    date_now_year = date_now.year * 1
    count = 0
    while first_cup_year < date_now_year:
        count += 1
        first_cup_year += 4
    if count < titles:
        raise ImpossibleTitlesError("impossible to have more titles than disputed cups")


class TeamView(APIView):
    def post(self, request):
        try:
            validate_first_cup(request.data["first_cup"])
        except InvalidYearCupError:
            return Response({"error": "there was no world cup this year"}, 400)
        try:
            validate_titles(request.data["titles"])
        except NegativeTitlesError:
            return Response({"error": "titles cannot be negative"}, 400)
        try:
            validate_titles_years(request.data["titles"], request.data["first_cup"])
        except ImpossibleTitlesError:
            return Response(
                {"error": "impossible to have more titles than disputed cups"}, 400
            )
        team_data = request.data
        team = Team.objects.create(**team_data)
        return Response(model_to_dict(team), 201)

    def get(self, request):
        teams = Team.objects.all()

        teams_dict = []

        for team in teams:
            t = model_to_dict(team)
            teams_dict.append(t)

        return Response(teams_dict)


class TeamsDetailedView(APIView):
    def get(self, request, account_id):
        try:
            teams = Team.objects.get(pk=account_id)
        except Team.DoesNotExist:
            return Response({"message": "Team not found"}, 404)
        team_dict = model_to_dict(teams)
        return Response(team_dict)

    def patch(self, request, account_id):
        try:
            teams = Team.objects.get(pk=account_id)
        except Team.DoesNotExist:
            return Response({"message": "Team not found"}, 404)
        team_data = request.data
        for field in team_data:
            setattr(teams, field, team_data[field])
        teams.save()
        return Response(model_to_dict(teams))

    def delete(self, request, account_id):
        try:
            teams = Team.objects.get(pk=account_id).delete()
        except Team.DoesNotExist:
            return Response({"message": "Team not found"}, 404)

        return Response(status=204)
