from flask import Flask, request, abort
from flask_restful import abort, Api, Resource
from flask_cors import CORS
from marshmallow import Schema, fields
from translatepy import Translator
from translatepy.translators import BingTranslate, ReversoTranslate, TranslateComTranslate, GoogleTranslate, DeeplTranslate
from translatepy.exceptions import TranslatepyException, UnknownLanguage
import urllib3

urllib3.disable_warnings()

class QuerySchema(Schema):
    q = fields.Str(required=True)
    tl = fields.Str(required=True)

app = Flask(__name__)

# host in NAS and add cors
cors = CORS(app, origins=["http://127.0.0.1:5500", "https://multilang.joeper.myds.me"])

api = Api(app)
schema = QuerySchema()
t_services = Translator(services_list=[BingTranslate, ReversoTranslate, TranslateComTranslate, GoogleTranslate])
d_services = Translator(services_list=[ReversoTranslate, BingTranslate, GoogleTranslate])

class Dictionary(Resource):
        
    def dictionaryeHandler(self, text, tl):

        result = ""

        try:
            result = d_services.dictionary(text, destination_language=tl)
        except UnknownLanguage as err:
            print("An error occured while searching for the language you passed in")
            print("Similarity:", round(err.similarity), "%")
            return
        except TranslatepyException:
            print("An error occured while translating with translatepy")
            return
        except Exception:
            print("An unknown error occured")
            return
        
        print("service used: " + str(result.service))
        
        return result

    def get(self):

        # check args are received
        errors = schema.validate(request.args)
        if errors:
            abort(400, message=str(errors))

        query = request.args.get('q')
        tl = request.args.get('tl')

        # print(query)
        # print(tl)

        q = self.dictionaryeHandler(query, tl)
        

        if q is None or len(q.result) <= 0:
            print("An error occured while translating with translatepy")
            abort(400, message=str("No results for query: " + query))

        res = {
            "service": str(q.service),
            "result": q.result
        }

        return res

class Translate(Resource):

    def translateHandler(self, text, tl):

        result = ""

        try:
            result = t_services.translate(text, destination_language=tl)
        except UnknownLanguage as err:
            print("An error occured while searching for the language you passed in")
            print("Similarity:", round(err.similarity), "%")
            return
        except TranslatepyException:
            print("An error occured while translating with translatepy")
            return
        except Exception:
            print("An unknown error occured")
            return
        
        print("service used: " + str(result.service))
        
        return result


    def get(self):

        errors = schema.validate(request.args)
        if errors:
            abort(400, message=str(errors))

        query = request.args.get('q')
        tl = request.args.get('tl')

        print(query)
        print(tl)
        
        q = self.translateHandler(query, tl)
        

        if q is None or len(q.result) <= 0:
            print("An error occured while translating with translatepy")
            abort(400, message=str("No results for query: " + query))

        res = {
            "service": str(q.service),
            "result": str(q.result)
        }

        return res

api.add_resource(Dictionary, '/dictionary', endpoint='dict')
api.add_resource(Translate, '/translate', endpoint='translate')

# omit of you intend to use `flask run` command
if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='server.log',level=logging.INFO)
    app.run(debug=True, port=8662)














