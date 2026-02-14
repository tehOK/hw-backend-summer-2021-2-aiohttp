from marshmallow import Schema, fields


class AdminSchema(Schema):
    email = fields.Str(required=True, example="admin@admin.com")
    password = fields.Str(required=True, example="admin")


class AdminResponseSchema(Schema):
    id = fields.Int(required=True)
    email = fields.Str(required=True)
