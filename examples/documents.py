from pydantic import BaseModel, ValidationError

from pyjas.v1_1.jsonapi_builder import Document, RelationshipObject, ResourceIdentifierObject, ResourceObject


class AuthorModel(BaseModel):
    id: int
    firstName: str
    lastName: str
    twitter: str | None = None
    __type__ = 'people'


class ArticleModel(BaseModel):
    id: int
    title: str
    __type__ = 'articles'


# Valid Document: document with single resource object

# Create model instances
author = AuthorModel(id=9, firstName='Dan', lastName='Gebhardt', twitter='dgeb')
article = ArticleModel(id=1, title='JSON API paints my bikeshed!')

# Create ResourceObjects
lid_registry = {}
author_resource = ResourceObject.from_model(
    model=author, links={'self': 'http://example.com/people/9'}, lid_registry=lid_registry
)

article_resource = ResourceObject.from_model(
    model=article,
    relationships={
        'author': RelationshipObject(
            links={
                'self': 'http://example.com/articles/1/relationships/author',
                'related': 'http://example.com/articles/1/author',
            },
            data=ResourceIdentifierObject(type='people', id='9'),
        )
    },
    links={'self': 'http://example.com/articles/1'},
    included=[author_resource],
    lid_registry=lid_registry,
)

# Construct the Document
document = Document(
    data=article_resource, included=[author_resource], meta={'copyright': 'Copyright 2024 Example Corp.'}
)

print(document.json(indent=2))


# Invalid Document: conflicing names
try:
    article_invalid = ResourceObject(
        type_='articles',
        id_='2',
        attributes={'title': 'Another Article', 'author': 'Should not be here'},
        relationships={'author': RelationshipObject(data=ResourceIdentifierObject(type='people', id='10'))},
    )
except ValidationError as e:
    print(e)

# Invalid Document: reserved attribute name
try:
    article_reserved = ResourceObject(
        type_='articles', id_='3', attributes={'title': 'Reserved Attribute', 'type': 'should not be here'}
    )
except ValidationError as e:
    print(e)

# Invalid Document: invalid relationship object, missing required members
try:
    invalid_relationship = RelationshipObject()
except ValidationError as e:
    print(e)

# Invalid Document: invalid links, unsupported link key
try:
    article_invalid_link = ResourceObject(
        type_='articles',
        id_='4',
        attributes={'title': 'Invalid Link'},
        links={'unsupported_link': 'http://example.com/invalid'},
    )
except ValidationError as e:
    print(e)
