# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 13:24:43 2023

@author: kgordillo
"""

import json
import boto3
import logging
import time
import flask
import math
import numpy as np
import os

from flask import Response, request
from soundfile import SoundFile
from Acoustics import Acoustics
from Correction import apply_correction_filter


application = flask.Flask(__name__)

s3 = boto3.client("s3")

application.logger.setLevel(logging.DEBUG)

rec_seconds = 60
db_offset = 27.45
calibration = math.pow(10, db_offset/20)


bands = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315,
         400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000,
         5000, 6300, 8000, 10000, 12500, 16000, 20000]
gains = [-1.4, -3.8, -4.6, -5.1, -4.2, -2.3, -0.2, -0.3, -0.9, 0.2, 0.4, 0.2, 0.4, 0, -0.6, -0.8, -1.3, -1.8, -1.5, -0.7, -0.6, -1.8, -3.6, -8.1, -10.3, -8.4, -3, -0.6, -4.1, -4.2, -0.1, -2.3, -2.7]


for g in range(len(gains)):
    gains[g] = gains[g] + 1.7

path = "/tmp"


@application.route("/soundMetrics", methods=["POST"])
def identify_sound():
    
    start_time = time.time()
    logging.debug('Calculador de métricas iniciado...')
    
    response = None
    out_file_path = ''
    if request.json is None:
        # Expect application/json request
        response = Response("Empty request", status=415)
    else:
        request_content = json.loads(request.data)
        try:
            content_json = json.loads(request_content["Message"])

            if request_content["TopicArn"] and request_content["Message"]:
                message = content_json["Records"][0]["s3"]
            else:
                message = request_content
                
            bucket = message["bucket"]["name"]
            archivo = message["object"]["key"]
            
            tmp_prnt = "Descargar el archivo: " + archivo + " del bucket: " + bucket
            
            out_file_path = path + '/' + str(archivo)
            logging.warn(tmp_prnt)

            s3.download_file(Bucket=bucket, Key=archivo, Filename=out_file_path)
            
            logging.warn("Inicializa el calculador de metricas")
            
            result = calcular_metricas(str(archivo))

            logging.warn("Finaliza el calculador de metricas")

            processing_time = (time.time() - start_time)
            file_date = get_file_date(str(archivo))
            file_hour = get_file_hour(str(archivo))

            service_response = {
                'ProcessingTime_seconds': processing_time,
                'Audio_fecha': file_date,
                'Audio_hora': file_hour,
                'Metrics_result': result
            }
            logging.warn("Files in tmp before:")
            list_directory(path)
            #Removing file
            os.remove(out_file_path)
            logging.warn("Files in tmp after:")
            list_directory(path)
            s3.put_object(
                Body=(bytes(json.dumps(service_response).encode('UTF-8'))),
                Bucket='soundmonitor-noise-level',
                Key='NoiseLevel_'+str(archivo)+'_.json'
            )

            response = Response("Metrics calculation completed", status=200)
            logging.warn("Response saved in S3....")
        except Exception as ex:
            response = s3.put_object(
                Body=(bytes(json.dumps({'statusCode': 500, 'error_processing': request.json,
                                        'exception': str(ex)}).encode('UTF-8'))),
                Bucket='soundmonitor-error-logs',
                Key='NoiseLevel_' + str(archivo) + '_error.json'
            )
            if out_file_path:
                os.remove(out_file_path)
            logging.exception("Error processing message: %s" % request.json)
            logging.exception(ex)
    
    return response


def calcular_metricas(file_name):
    try:
        audio_file = SoundFile(path+"/"+file_name)
        data = np.asarray(audio_file.read())

        sample_rate = audio_file.samplerate
        num_channels = audio_file.channels
        audio_file.close()
        print("Applying correction filter")
        data = apply_correction_filter(data, bands, gains, sample_rate)

        print("Measuring A...")
        measurement_A = Acoustics(filename=file_name,
                                  signal=data,
                                  fs=sample_rate,
                                  channels=num_channels,
                                  cal_factor=calibration,
                                  weighting='A'
                                  )

        return measurement_A.compute_parameters()

    except RuntimeError as re:
        logging.exception("--- Couldn't open : %s" % file_name)
        logging.exception(re)
        raise


def list_directory(dir_path):
    for file in os.listdir(dir_path):
        # check only text files
        if file.endswith('.wav'):
            logging.warn(file)


def get_file_date(file_name):
    date_split = file_name.split("_")
    if len(date_split) > 1:
        return date_split[1] + ""
    else:
        return ""


def get_file_hour(file_name):
    date_split = file_name.split("_")
    if len(date_split) > 2:
        return date_split[2] + ""
    else:
        return ""


@application.route("/")
def print_hello():
    response = Response("Hello", status=200)
    return response


if __name__ == "__main__":
    application.run(host="0.0.0.0", threaded=False)