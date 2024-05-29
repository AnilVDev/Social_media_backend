import graphene
import post_app.schema
import authentication.schema

class Query(authentication.schema.Query, post_app.schema.Query,graphene.ObjectType):
    pass

class Mutation(post_app.schema.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation = Mutation)