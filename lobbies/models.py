import json
from django.db import models
from .utils import (
    generate_id,
    generate_short_url,
    generate_security_token,
    send_group_message,
)
from rest_framework import exceptions
from django.utils import timezone


class AbstractBaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, default=generate_id, unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Lobby(AbstractBaseModel):
    name = models.CharField(max_length=100)

    url_code = models.CharField(
        max_length=100, editable=False, default=generate_short_url
    )

    # Status of the lobby
    WAITING = "waiting"
    ACTIVE = "active"
    FINISHED = "finished"
    STATUS_CHOICES = [
        (WAITING, "Waiting"),
        (ACTIVE, "Active"),
        (FINISHED, "Finished"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=WAITING,
    )

    max_players = models.IntegerField()

    security_token = models.CharField(
        max_length=100, editable=False, default=generate_security_token, unique=True
    )

    game_started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)

    questions = models.ManyToManyField("Question", blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = generate_id()
        if self.security_token is None:
            self.security_token = generate_security_token()
        if self.url_code is None:
            self.url_code = generate_short_url()
        super(Lobby, self).save(*args, **kwargs)

    def get_question(self):
        question = (
            Question.objects.exclude(id__in=self.questions.all()).order_by("?").first()
        )
        if question is None:
            raise exceptions.NotAcceptable("No more questions")

        self.questions.add(question)

        send_group_message(
            f"lobby_{self.id}",
            "new question",
            {
                "question": question.text,
                "id": str(question.id),
            },
        )
        return question

    def start_game(self):
        if self.status != Lobby.WAITING:
            raise exceptions.NotAcceptable("Cannot start game that is not waiting")
        self.status = Lobby.ACTIVE
        self.game_started_at = timezone.now()
        self.save()

        send_group_message(
            f"lobby_{self.id}",
            "game started",
            {
                "lobby": self.name,
            },
        )

        self.get_question()

        return self

    def finish_game(self):
        if self.status != Lobby.ACTIVE:
            raise exceptions.NotAcceptable("Cannot finish game that is not active")
        self.status = Lobby.FINISHED
        self.finished_at = timezone.now()
        self.save()

        send_group_message(
            f"lobby_{self.id}",
            "game finished",
            {
                "lobby": self.name,
            },
        )

        return self

    def answer_question(self, question_id, answer, player):
        if self.status != Lobby.ACTIVE:
            raise exceptions.NotAcceptable(
                "Cannot answer question in game that is not active"
            )
        question = Question.objects.get(id=question_id)
        if question is None:
            raise exceptions.NotAcceptable("Question does not exist")
        answer = Answer.objects.create(
            text=answer,
            question=question,
            player=player,
            lobby=self,
        )
        answer.save()

        total_players = self.player_set.count()
        answers = Answer.objects.filter(question=question, lobby=self)
        answers_count = answers.count()

        if answers_count >= total_players:
            # Directly construct the dictionary expected by send_group_message
            answers_data = {
                "answers": [
                    {"text": answer.text, "player": answer.player.name}
                    for answer in answers
                ],
            }
            send_group_message(f"lobby_{self.id}", "all answers received", answers_data)

        send_group_message(
            f"lobby_{self.id}",
            "new answer",
            {
                "answer": answer.text,
                "player": player.name,
                "remaining": total_players - answers_count,
            },
        )

        return self

    def get_answers(self, question_id):
        if self.status != Lobby.ACTIVE:
            raise exceptions.NotAcceptable(
                "Cannot get answers in game that is not active"
            )
        question = Question.objects.get(id=question_id)
        if question is None:
            raise exceptions.NotAcceptable("Question does not exist")
        # Get the answers for the specified question in the lobby
        answers = Answer.objects.filter(question=question, lobby=self)
        return answers


class Player(AbstractBaseModel):
    name = models.CharField(max_length=100)

    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, null=True)

    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = generate_id()
        super(Player, self).save(*args, **kwargs)

    def join_lobby(self, lobby):
        if self.lobby is not None:
            raise exceptions.NotAcceptable("Player is already in a lobby")
        if lobby.status != Lobby.WAITING:
            raise exceptions.NotAcceptable("Cannot join lobby that is not waiting")
        if lobby.max_players <= lobby.player_set.count():
            raise exceptions.NotAcceptable("Cannot join lobby that is full")

        self.lobby = lobby
        self.save()

        send_group_message(
            f"lobby_{self.lobby.id}",
            "joined lobby",
            {
                "player": self.name,
            },
        )

        return lobby.security_token

    def leave_lobby(self):
        self.lobby = None
        self.save()

        send_group_message(
            f"lobby_{self.lobby.id}",
            "left lobby",
            {
                "player": self.name,
            },
        )
        return self


class Question(AbstractBaseModel):
    text = models.CharField(max_length=1000)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = generate_id()
        super(Question, self).save(*args, **kwargs)


class Answer(AbstractBaseModel):
    text = models.CharField(max_length=1000)

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = generate_id()
        super(Answer, self).save(*args, **kwargs)
