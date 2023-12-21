import aiohttp
from fastapi import APIRouter, Response
from typing import List

from fastapi.encoders import jsonable_encoder

from api.models.navegacion import AutocompletadoModel, NavegacionRequestModel


router = APIRouter(prefix="/navegacion")

GRAPHQL_ENDPOINT = "http://opentripplanner:8080/otp/routers/default/index/graphql"


@router.post("/", response_description="Obtener plan de navegacion", response_model=object, response_model_exclude_none=True)
async def get_plan_navegacion(peticion: NavegacionRequestModel, response: Response):
  try:
    query = """
      query ($fecha: String, $hora: String, $origen: InputCoordinates!, $destino: InputCoordinates!, $accesibleSillaDeRuedas: Boolean, $respuestaMaxItinerarios: Int, $cursorPagina: String, $llegada: Boolean, $locale: String) {
        plan(
          date: $fecha
          time: $hora
          from: $origen
          to: $destino
          wheelchair: $accesibleSillaDeRuedas
          numItineraries: $respuestaMaxItinerarios
          pageCursor: $cursorPagina
          arriveBy: $llegada
          locale: $locale
        ) {
          date
          from {
            name
            lat
            lon
          }
          to {
            name
            lat
            lon
          }
          itineraries {
            startTime
            endTime
            duration
            waitingTime
            walkTime
            walkDistance
            legs {
              startTime
              endTime
              departureDelay
              arrivalDelay
              mode
              duration
              legGeometry {
                length
                points
              }
              agency {
                gtfsId
                name
              }
              realTime
              realtimeState
              distance
              transitLeg
              walkingBike
              from {
                name
                lat
                lon
                arrivalTime
                departureTime
              }
              to {
                name
                lat
                lon
                arrivalTime
                departureTime
              }
              route {
                gtfsId
                shortName
                longName
                mode
                type
                color
                textColor
                bikesAllowed
              }
              trip {
                gtfsId
                tripShortName
                tripHeadsign
                shapeId
                wheelchairAccessible
                bikesAllowed
              }
              intermediatePlaces {
                name
                lat
                lon
                arrivalTime
                departureTime
              }
              intermediatePlace
              steps {
                distance
                relativeDirection
                streetName
                stayOn
                bogusName
              }
              headsign
              pickupType
              dropoffType
            }
            accessibilityScore
            numberOfTransfers
            fares {
              type
              currency
              cents
            }
          }
        }
      }"""

    headers = {
      "OTPTimeout": "180000",
      "Content-Type": "application/json"
    }
    datos = {
      "query": query,
      "variables": jsonable_encoder(peticion)
    }
    async with aiohttp.ClientSession() as session:
      async with session.post(GRAPHQL_ENDPOINT, headers=headers, json=datos) as respuesta:
        return await respuesta.json()
  except:
    response.status_code = 500
    return []