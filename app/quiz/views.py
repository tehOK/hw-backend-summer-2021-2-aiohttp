from aiohttp import web_exceptions as exc
from aiohttp_apispec import docs, request_schema, response_schema

from app.quiz.schemes import (
    AnswerSchema,
    ListQuestionSchema,
    QuestionResponseSchema,
    QuestionSchema,
    ThemeCreateSchema,
    ThemeListSchema,
    ThemeResponseSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @docs(
        tags=["Quiz"],
        summary="Добавить тему",
        description="Добавить тему для вопросов викторины",
    )
    @request_schema(ThemeCreateSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        theme_title = self.data.get("title")
        if await self.store.quizzes.get_theme_by_title(title=theme_title):
            raise exc.HTTPConflict(reason="Тема с таким именем уже существует")
        theme = await self.store.quizzes.create_theme(title=theme_title)
        self.store.quizzes.logger.info("Созданная новая тема для квиза %s", theme_title)
        return json_response(data=ThemeResponseSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @docs(
        tags=["Quiz"],
        summary="Список тем",
        description="Получить список всех тем викторины",
    )
    @response_schema(OkResponseSchema(many=True), 200)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @docs(
        tags=["Quiz"],
        summary="Добавить вопрос",
        description="Добавить вопрос для викторины",
    )
    @request_schema(QuestionSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        data = self.data

        if not await self.store.quizzes.get_theme_by_id(id_=data["theme_id"]):
            raise exc.HTTPNotFound(reason="Тема не найдена")
        if await self.store.quizzes.get_question_by_title(title=data["title"]):
            raise exc.HTTPConflict(
                reason="Вопрос с таким именем уже существует"
            )
        if len(data["answers"]) < 2:
            raise exc.HTTPBadRequest(reason="Должно быть не менее 2 ответов")
        if sum(answer["is_correct"] for answer in data["answers"]) != 1:
            raise exc.HTTPBadRequest(
                reason="Должен быть ровно один правильный ответ"
            )

        answers = [AnswerSchema().load(answer) for answer in data["answers"]]

        question = await self.store.quizzes.create_question(
            title=data["title"], theme_id=data["theme_id"], answers=answers
        )
        return json_response(data=QuestionResponseSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @docs(
        tags=["Quiz"],
        summary="Список вопросов",
        description="Получить список всех вопросов викторины, с возможностью фильтрации по теме",
    )
    @response_schema(OkResponseSchema(many=True), 200)
    async def get(self):
        theme_id = self.request.query.get("theme_id")
        if theme_id and not await self.store.quizzes.get_theme_by_id(
            id_=theme_id
        ):
            raise exc.HTTPNotFound(reason="Тема не найдена")
        questions = await self.store.quizzes.list_questions(theme_id=theme_id)
        return json_response(
            data=ListQuestionSchema().dump({"questions": questions})
        )
