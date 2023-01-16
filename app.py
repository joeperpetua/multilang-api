from flask import Flask, request, abort
from flask_restful import Api, Resource
from flask_cors import CORS
from marshmallow import Schema, fields
from translatepy import Translator
from translatepy.translators import BingTranslate, ReversoTranslate, TranslateComTranslate, GoogleTranslate, DeeplTranslate
from translatepy.exceptions import TranslatepyException, UnknownLanguage
import flask_monitoringdashboard as dashboard
import urllib3
import regex

urllib3.disable_warnings()

class QuerySchema(Schema):
    q = fields.Str(required=True)
    tl = fields.List(fields.Str(), required=True)

app = Flask(__name__)
dashboard.config.init_from(file='./config.cfg')
dashboard.bind(app)

# host in NAS and add cors
cors = CORS(app, origins=["http://127.0.0.1:5500", "https://multilang.joeper.myds.me", "https://joeperpetua.github.io"])

api = Api(app)
schema = QuerySchema()
td_default = Translator()
t_services = Translator(services_list=[BingTranslate, ReversoTranslate, TranslateComTranslate, GoogleTranslate])
d_services = Translator(services_list=[ReversoTranslate, BingTranslate, GoogleTranslate])

def validateArgs(q, tl, sl):
        if q is None or q == "":
            abort(400, "No query provided.")

        if tl is None or tl == "":
            abort(400, "No target language provided.")
        
        if sl is None or sl == "":
            abort(400, "No source language provided.")

class Dictionary(Resource):
        
    def dictionaryHandler(self, text, tl, sl):
        result = ""
        try:
            result = d_services.dictionary(text, destination_language=tl, source_language=sl)
        except UnknownLanguage as err:
            print(f"Could not translate due to {UnknownLanguage}. Continue to use default service.")
            return None
        except TranslatepyException:
            print(f"Could not translate due to {TranslatepyException}. Continue to use default service.")
            return None
        except Exception:
             print(f"Could not translate due to {Exception}. Continue to use default service.")
             return None
        return result

    def dictionaryDefault(self, text, tl, sl):
        result = ""
        try:
            result = td_default.dictionary(text, destination_language=tl, source_language=sl)
        except UnknownLanguage as err:
            abort(400, f"An error occured while searching for the language you passed in. Similarity: {round(err.similarity)}")
        except TranslatepyException:
            abort(500, "An error occured while translating with translatepy")
        except Exception:
            abort(500, "An unknown error occured")
        return result

    def get(self):
        validateArgs(request.args.get('q'), request.args.get('tl'), request.args.get('sl')) 
        query = request.args.get('q')
        pre_format_tl = request.args.get('tl')
        sl = request.args.get('sl')
        tl = pre_format_tl.split(",")

        response = []
        total_length = 0

        for language in tl:
            translation = self.dictionaryHandler(query, language, sl)
            if translation is None or len(translation.result) <= 0:
                translation = self.dictionaryDefault(query, language, sl)
            
            if translation is None or len(translation.result) <= 0:
                pass
            else:
                total_length += 1
                response.append({
                    "source": str(translation.source_language),
                    "target": str(translation.destination_language),
                    "service": str(translation.service),
                    "result": translation.result
                })   

        if total_length <= 0:
            abort(400, f"No results for query: {query}")

        return {"definitions": response}

class Translate(Resource):

    def translateHandler(self, text, tl, sl, html):
        result = ""
        try:
            if html:
                result = td_default.translate_html(text, destination_language=tl, source_language=sl)
            else:
                result = td_default.translate(text, destination_language=tl, source_language=sl)     
        except UnknownLanguage as err:
            print(f"Could not translate due to {UnknownLanguage}. Continue to use default service.")
            return None
        except TranslatepyException:
            print(f"Could not translate due to {TranslatepyException}. Continue to use default service.")
            return None
        except Exception:
             print(f"Could not translate due to {Exception}. Continue to use default service.")
             return None     
        return result
    
    def translateDefault(self, text, tl, sl, html):
        result = ""

        try:
            if html:
                result = td_default.translate_html(text, destination_language=tl, source_language=sl)
            else:
                result = td_default.translate(text, destination_language=tl, source_language=sl)
        except UnknownLanguage as err:
            abort(400, f"An error occured while searching for the language you passed in. Similarity: {round(err.similarity)}")
        except TranslatepyException:
            abort(500, "An error occured while translating with translatepy")
        except Exception:
            abort(500, "An unknown error occured") 
        return result

    def get(self):
        validateArgs(request.args.get('q'), request.args.get('tl'), request.args.get('sl'))
        query = request.args.get('q')
        pre_format_tl = request.args.get('tl')
        sl = request.args.get('sl')
        tl = pre_format_tl.split(",")

        response = []
        total_length = 0

        for language in tl:
            translation = self.translateHandler(query, language, sl, False)
            if translation is None or len(translation.result) <= 0:
                translation = self.translateDefault(query, language, sl, False)
            
            if translation is None or len(translation.result) <= 0:
                pass
            else:
                total_length += 1
                response.append({
                    "source": str(translation.source_language),
                    "target": str(translation.destination_language),
                    "service": str(translation.service),
                    "result": translation.result
                })   

        if total_length <= 0:
            abort(400, f"No results for query: {query}")

        return {"translations": response}
    
    
    def post(self):
        validateArgs(request.form.get('q'), request.form.get('tl'), request.form.get('sl'))
        query = request.form.get('q')
        pre_format_tl = request.form.get('tl')
        sl = request.form.get('sl')
        tl = pre_format_tl.split(",")

        response = []
        total_length = 0

        for language in tl:
            translation = self.translateHandler(query, language, sl, True)
            if translation is None or len(translation) <= 0:
                translation = self.translateDefault(query, language, sl, True)
            
            if translation is None or len(translation) <= 0:
                pass
            else:
                translation = regex.sub(f'\"', "'", translation)
                total_length += 1
                response.append({
                    "source": str(sl),
                    "target": str(language),
                    "result": f'{translation}'
                })

        if total_length <= 0:
            abort(400, f"No results for query: {query}")

        return {"translations": response}

api.add_resource(Dictionary, '/dictionary', endpoint='dict')
api.add_resource(Translate, '/translate', endpoint='translate')

# omit of you intend to use `flask run` command
if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='server.log',level=logging.ERROR)
    app.run(debug=False, port=8662)














