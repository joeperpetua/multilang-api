from dataclasses import Field
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
    tl = fields.List(fields.Str(), required=True)

app = Flask(__name__)

# host in NAS and add cors
cors = CORS(app, origins=["http://127.0.0.1:5500", "https://multilang.joeper.myds.me"])

api = Api(app)
schema = QuerySchema()
t_services = Translator(services_list=[BingTranslate, ReversoTranslate, TranslateComTranslate, GoogleTranslate])
d_services = Translator(services_list=[ReversoTranslate, BingTranslate, GoogleTranslate])

def validateArgs(q, tl):
        if q is None or q == "":
            abort(400, message="No query provided")

        if tl is None or tl == "":
            abort(400, message="No target language provided")

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

        validateArgs(request.args.get('q'), request.args.get('tl'))
        
        query = request.args.get('q')
        pre_format_tl = request.args.get('tl')
        tl = pre_format_tl.split(",")

        print("----------making request for: ----------\n", query)
        print(tl)

        q = []
        total_length = 0

        q = []
        total_length = 0

        for e in tl:
            #print("-----", e)
            tmp = self.dictionaryeHandler(query, e)
            if tmp is None or len(tmp.result) <= 0:
                pass
            else:
                total_length += 1
                q.append({
                    "target": str(e),
                    "service": str(tmp.service),
                    "result": tmp.result
                })   

        if total_length <= 0:
            print("An error occured while translating with translatepy")
            abort(400, message=str("No results for query: " + query))

        return {"definitions": q}

class Translate(Resource):



    def translateHandler(self, text, tl):

        result = ""

        try:
            result = t_services.translate(text, destination_language=tl)
        except UnknownLanguage as err:
            print("An error occured while searching for the language you passed in", tl)
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
        validateArgs(request.args.get('q'), request.args.get('tl'))
        
        query = request.args.get('q')
        pre_format_tl = request.args.get('tl')
        tl = pre_format_tl.split(",")

        print("----------making request for: ----------\n", query)
        print(tl)

        q = []
        total_length = 0

        for e in tl:
            #print("-----", e)
            tmp = self.translateHandler(query, e)
            if tmp is None or len(tmp.result) <= 0:
                pass
            else:
                total_length += 1
                q.append({
                    "target": str(e),
                    "service": str(tmp.service),
                    "result": str(tmp.result)
                })   

        if total_length <= 0:
            print("An error occured while translating with translatepy")
            abort(400, message=str("No results for query: " + query))

        return {"translations": q}

api.add_resource(Dictionary, '/dictionary', endpoint='dict')
api.add_resource(Translate, '/translate', endpoint='translate')

# omit of you intend to use `flask run` command
if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='server.log',level=logging.ERROR)
    app.run(debug=True, port=8662)














