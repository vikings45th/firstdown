export default defineEventHandler(async (event) => {
  const requestBody = await readBody(event); //requestBody: {mood: mood.value, distance: distance.value},

  const resmsg = requestBody.mood + "気分で" + requestBody.distance + "km歩きたいとのことです"

  const dummyRouteRes = {
    mood : `${requestBody.mood}な気分`,
    title : "静寂のリバーサイドウォーク",
    polyline : [
      { lat: 37.772, lng: -122.214 },
      { lat: 21.291, lng: -157.821 },
      { lat: -18.142, lng: 178.431 },
      { lat: -27.467, lng: 153.027 },
    ],
    distance_km : requestBody.distance,
    duration_min : Math.round(requestBody.distance/0.06),
    steps : requestBody.distance*1000,
    summary : "信号の少ない川沿いの一本道。一定のリズムで歩くことで、頭の中を整理することができます。",
    spots : ["水面に映る夕日","長く続く遊歩道","静かな橋の下"]
  }
  
    /*
    return GenerateRouteResponse(
      request_id=req.request_id,
      route={
          "polyline": chosen.get("polyline", "xxxx"),
          "distance_km": float(chosen.get("distance_km", req.distance_km)),
          "duration_min": int(chosen.get("duration_min") or 32),
          "summary": summary,
          "spots": spots,
      },
      meta=meta,
    )
    */

  return {
    statusCode: 200,
    body: dummyRouteRes,
  }
})