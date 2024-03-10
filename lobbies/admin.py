from django.contrib import admin
from .models import Lobby, Player, Question, Answer


class LobbyAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "url_code", "created_at", "finished_at")
    readonly_fields = (
        "id",
        "security_token",
        "url_code",
        "created_at",
        "finished_at",
        "game_started_at",
        "players_count",
    )
    list_filter = ("status",)
    fieldsets = (
        (
            "Lobby Details",
            {
                "fields": (
                    "id",
                    "name",
                    "status",
                    "url_code",
                    "security_token",
                    "max_players",
                    "players_count",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "game_started_at", "finished_at")}),
        ("Questions", {"fields": ("questions",)}),
    )

    def players_count(self, obj):
        return obj.player_set.count()

    players_count.short_description = "Player Count"


class PlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "lobby")
    readonly_fields = ("id", "joined_at")
    list_filter = ("lobby",)
    fieldsets = (
        (
            "Player Details",
            {"fields": ("id", "name", "lobby", "joined_at")},
        ),
    )


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text")
    readonly_fields = ("id",)
    fieldsets = (
        (
            "Question Details",
            {"fields": ("id", "text")},
        ),
    )


admin.site.register(Lobby, LobbyAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
