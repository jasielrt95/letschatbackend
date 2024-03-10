from rest_framework import serializers
from .models import Lobby, Player, Question, Answer


class LobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lobby
        fields = (
            "id",
            "name",
            "status",
            "max_players",
            "created_at",
            "game_started_at",
            "finished_at",
            "security_token",
            "url_code",
        )
        read_only_fields = (
            "id",
            "created_at",
            "game_started_at",
            "finished_at",
            "security_token",
        )


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("id", "name", "lobby", "joined_at")
        read_only_fields = ("id", "joined_at", "lobby")


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "text", "created_at")
        read_only_fields = ("id", "created_at")


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ("id", "text", "question", "player", "lobby", "created_at")
        read_only_fields = ("id", "question", "player", "lobby", "created_at")
