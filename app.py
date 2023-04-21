from flask import Flask, request, abort
from flask_restful import Api, Resource
from flask_cors import CORS
from marshmallow import Schema, fields
from translatepy import Translator, Language
from translatepy.translators import BingTranslate, ReversoTranslate, GoogleTranslateV2, DeeplTranslate
from translatepy.exceptions import TranslatepyException, UnknownLanguage, NoResult
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
default_service = Translator()
translate_short_service = Translator(services_list=[GoogleTranslateV2, BingTranslate, ReversoTranslate])
translate_long_service = Translator(services_list=[DeeplTranslate, GoogleTranslateV2, BingTranslate, ReversoTranslate])
dictionary_service = Translator(services_list=[ReversoTranslate, GoogleTranslateV2, BingTranslate])
reverso_service = ReversoTranslate()
google_service = GoogleTranslateV2()

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
            result = dictionary_service.dictionary(text, destination_language=tl, source_language=sl)
        except UnknownLanguage as err:
            print(f"Could not translate due to {err}. Continue to use default service.")
            return None
        except TranslatepyException as err:
            print(f"Could not translate due to {err}. Continue to use default service.")
            return None
        except Exception as err:
             print(f"Could not translate due to {err}. Continue to use default service.")
             return None     
        return result

    def dictionaryDefault(self, text, tl, sl):
        result = ""
        try:
            result = default_service.dictionary(text, destination_language=tl, source_language=sl)
        except UnknownLanguage as err:
            abort(400, f"An error occured while searching for the language you passed in. Similarity: {round(err.similarity)}. Stack trace: {err}")
        except TranslatepyException as err:
            abort(500, f"An error occured while translating with translatepy. Stack trace: {err}")
        except Exception as err:
            abort(500, f"An unknown error occured. Stack trace: {err}") 
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
                result = google_service.translate_html(text, destination_language=tl, source_language=sl)
            else:
                if len(text) < 100:
                    result = translate_short_service.translate(text, destination_language=tl, source_language=sl)
                else:
                    result = translate_long_service.translate(text, destination_language=tl, source_language=sl)
        except UnknownLanguage as err:
            print(f"Could not translate due to {err}. Continue to use default service. Params: {text}, {tl}, {sl}, {html}")
            return None
        except TranslatepyException as err:
            print(f"Could not translate due to {err}. Continue to use default service. Params: {text}, {tl}, {sl}, {html}")
            return None
        except Exception as err:
             print(f"Could not translate due to {err}. Continue to use default service.")
             return None
        return result
    
    def translateDefault(self, text, tl, sl, html):
        result = ""

        try:
            if html:
                result = default_service.translate_html(text, destination_language=tl, source_language=sl)
            else:
                result = default_service.translate(text, destination_language=tl, source_language=sl)
        except NoResult as err:
            print(f"Could not translate due to {err}. Return query without translating. Params: {text}, {tl}, {sl}, {html}")
            return None
        except UnknownLanguage as err:
            abort(400, f"An error occured while searching for the language you passed in. Similarity: {round(err.similarity)}. Stack trace: {err}")
        except TranslatepyException as err:
            abort(500, f"An error occured while translating with translatepy. Stack trace: {err}")
        except Exception as err:
            abort(500, f"An unknown error occured. Stack trace: {err}") 
        return result

    def get(self):
        validateArgs(request.args.get('q'), request.args.get('tl'), request.args.get('sl'))
        query = request.args.get('q')
        pre_format_tl = request.args.get('tl')
        sl = request.args.get('sl')
        if sl == 'auto':
            sl = reverso_service.language(query).result
        tl = pre_format_tl.split(",")

        response = []

        for language in tl:
            # convert tl from String to Language to compare with sl
            current_tl = str(language)
            current_tl = Language(current_tl)

            # if tl and sl are the same, then return the result as it arrived
            if current_tl.id != sl.id:
                translation = self.translateHandler(query, current_tl, sl, False)
                if translation is None or len(translation.result) <= 0:
                    translation = self.translateDefault(query, current_tl, sl, False)
                                        
                # if translation comes empty due to NoResult error, then return as it arrived
                if translation is None or len(translation.result) <= 0:
                    response.append({
                        "source": str(sl),
                        "target": str(current_tl),
                        "service": "No service used.",
                        "result": str(query)
                    })
                else:
                    response.append({
                        "source": str(translation.source_language),
                        "target": str(translation.destination_language),
                        "service": str(translation.service),
                        "result": translation.result
                    })
            else:
                response.append({
                    "source": str(sl),
                    "target": str(current_tl),
                    "service": "No service used.",
                    "result": str(query)
                })
        return {"translations": response}
    
    def post(self):
        validateArgs(request.form.get('q'), request.form.get('tl'), request.form.get('sl'))
        query = request.form.get('q')
        pre_format_tl = request.form.get('tl')
        sl = request.form.get('sl')
        if sl == 'auto':
            sl = reverso_service.language(query).result
        tl = pre_format_tl.split(",")

        response = []

        for language in tl:
            # convert tl from String to Language to compare with sl
            current_tl = str(language)
            current_tl = Language(current_tl)
            
            # if tl and sl are the same, then return the result as it arrived
            if current_tl.id != sl.id:
                translation = self.translateHandler(query, current_tl, sl, True)
                if translation is None or len(translation) <= 0:
                    translation = self.translateDefault(query, current_tl, sl, True)

                # if translation comes empty due to NoResult error, then return as it arrived
                if translation is None or len(translation) <= 0:
                    response.append({
                        "source": str(sl),
                        "target": str(current_tl),
                        "service": "No service used.",
                        "result": str(query)
                    })
                else:
                    translation = regex.sub(f'\"', "'", translation)
                    response.append({
                        "source": str(sl),
                        "target": str(current_tl),
                        "result": f'{translation}'
                    })
            else:
                response.append({
                    "source": str(sl),
                    "target": str(current_tl),
                    "service": "No service used.",
                    "result": str(query)
                })
        return {"translations": response}

api.add_resource(Dictionary, '/dictionary', endpoint='dict')
api.add_resource(Translate, '/translate', endpoint='translate')
api.add_resource(Translate, '/djapones', endpoint='djapones')

# omit of you intend to use `flask run` command
if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='server.log',level=logging.ERROR)
    app.run(debug=False, port=8662)














