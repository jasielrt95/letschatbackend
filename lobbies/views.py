from rest_framework import viewsets, status, exceptions
from django.core.exceptions import ValidationError
from .models import Lobby, Player, Question, Answer
from .serializers import (
    LobbySerializer,
    PlayerSerializer,
    QuestionSerializer,
    AnswerSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response

class LobbyViewSet(viewsets.ModelViewSet):
    queryset = Lobby.objects.all()
    serializer_class = LobbySerializer

    @action(
        detail=True,
        methods=["post"],
        url_path="start",
    )
    def start(self, request, pk=None):
        # Get the security token from the request data, if it doesn't exist, raise an error
        security_token = request.data.get("security_token")
        if security_token != self.get_object().security_token:
            raise exceptions.NotAcceptable("Security token is invalid")
        lobby = self.get_object()
        if lobby is None:
            raise exceptions.AuthenticationFailed(
                "Lobby not found, authentication failed"
            )
        lobby.start_game()
        return Response({"message": "game started"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="finish")
    def finish(self, request, pk=None):
        lobby = self.get_object()
        lobby.finish_game()
        return Response({"message": "game finished"}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="questions/(?P<question_id>[^/.]+)/answer",
    )
    def answer(self, request, pk=None, question_id=None):
        # Get the security token from the request data, if it doesn't exist, raise an error
        security_token = request.data.get("security_token")
        if security_token != self.get_object().security_token:
            raise exceptions.NotAcceptable("Security token is invalid")

        # Get the answer from the request data, if it doesn't exist, raise an error
        answer = request.data.get("answer")
        if answer is None:
            raise exceptions.NotAcceptable("Answer is required")

        lobby = self.get_object()
        player = Player.objects.get(id=request.data.get("player_id"))
        lobby.answer_question(question_id, answer, player)
        return Response({"message": "question answered"}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["get"],
        url_path="questions/(?P<question_id>[^/.]+)/answer",
    )
    def get_answer(self, request, pk=None, question_id=None):
        # Get the security token from the request data, if it doesn't exist, raise an error
        security_token = request.data.get("security_token")
        if security_token != self.get_object().security_token:
            raise exceptions.NotAcceptable("Security token is invalid")

        lobby = self.get_object()
        answers = lobby.get_answers(question_id)
        serializer = AnswerSerializer(answers, many=True)
        return Response(
            {"message": "answers retrieved", "answers": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="questions/nextround",
    )
    def next_round(self, request, pk=None):
        # Get the security token from the request data, if it doesn't exist, raise an error
        security_token = request.data.get("security_token")
        if security_token != self.get_object().security_token:
            raise exceptions.NotAcceptable("Security token is invalid")

        lobby = self.get_object()
        lobby.get_question()
        return Response(
            {"message": "next round started"},
            status=status.HTTP_200_OK,
        )


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    @action(detail=True, methods=["post"], url_path="join")
    def join(self, request, pk=None):
        player = self.get_object()

        # Get the lobby ID from the request data, if it doesn't exist, raise an error
        lobby_id = request.data.get("lobby_id")
        if lobby_id is None:
            raise exceptions.NotAcceptable("Lobby ID is required")

        # Get the lobby from the database, if it doesn't exist or ID is not UUID, raise an error
        try:
            lobby = Lobby.objects.get(id=lobby_id)
        except Lobby.DoesNotExist:
            raise exceptions.NotFound("Lobby does not exist")
        except ValidationError:
            raise exceptions.ParseError("Lobby ID is invalid, must be UUID")

        serializer = LobbySerializer(lobby)

        # Finally, trigger the join_lobby method on the player
        security_token = player.join_lobby(lobby)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="leave")
    def leave(self, request, pk=None):
        player = self.get_object()
        player.leave_lobby()
        return Response({"message": "player left lobby"}, status=status.HTTP_200_OK)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
