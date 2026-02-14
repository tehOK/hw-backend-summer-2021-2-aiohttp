from marshmallow import Schema, fields


class ThemeSchema(Schema):
    title = fields.Str(required=True, example="Веб-программирование")


class ThemeCreateSchema(ThemeSchema):
    pass


class ThemeResponseSchema(ThemeSchema):
    id = fields.Int()


class ThemeListSchema(Schema):
    themes = fields.List(fields.Nested(ThemeResponseSchema))


class AnswerSchema(Schema):
    title = fields.Str(required=True, example="Ответ 1")
    is_correct = fields.Bool(required=True, example=True)


class QuestionSchema(Schema):
    title = fields.Str(required=True, example="Вопрос 1")
    theme_id = fields.Int(required=True, example=1)
    answers = fields.List(fields.Nested(AnswerSchema), required=True)


class QuestionCreateSchema(QuestionSchema):
    pass


class QuestionResponseSchema(QuestionSchema):
    id = fields.Int()


class ListQuestionSchema(Schema):
    questions = fields.List(fields.Nested(QuestionResponseSchema))
