import httpx


async def fetch_person_data(name: str):
    async with httpx.AsyncClient() as client:
        gender_resp = await client.get(
            "https://api.genderize.io", params={"name": name}
        )
        age_resp = await client.get("https://api.agify.io", params={"name": name})
        nat_resp = await client.get("https://api.nationalize.io", params={"name": name})

        gender = gender_resp.json().get("gender", "unknown")
        age = age_resp.json().get("age", 0)
        country_data = nat_resp.json().get("country", [])
        nationality = country_data[0]["country_id"] if country_data else "unknown"

        return {"gender": gender, "age": age, "nationality": nationality}
