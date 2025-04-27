import random
import pyanty as dolphin
from pyanty import DolphinAPI, STABLE_CHROME_VERSION

api = DolphinAPI(api_key='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNzJlMmVhNWU2N2QwMmIzYTkyMGFhYzE3OGU1YTJjNTZkYzk1ZDIzZjc5ZDk5MTY2YzA1MmJjNzg0OTI5MzAwZTJhMjA1OGFhMzFmNWM1ODEiLCJpYXQiOjE3NDI1MjU0NTkuMzA1NDA5LCJuYmYiOjE3NDI1MjU0NTkuMzA1NDEsImV4cCI6MTc3NDA2MTQ1OS4yOTc0LCJzdWIiOiIzNDYxNjY2Iiwic2NvcGVzIjpbXX0.Kz2SzeNrxawvyxfyF0vTIjxfROImi9kNz1vZSHyrg43gb_vuiybpYR-SBMGeEUpOT3yR9bjgEpO88cvGjeETKlw1n2a8uCITBs84vapAavqBEUvg7u5HEJ7dXLCMmxhq0D9Hn8daK6lxVd3ZuKr9yB92lxWZRcLV8vwK-xyrjEcAHNh41N3g4o_n0XknjN9chfYVOW0WvfqwPvEJ8ZmB4CBinfo7QYKWm8uv1zC5h5GOFKHRYHO1IYoYMnTbZVjj4lWeYHVn6NGPV2hgjVx9L1FeU7wghWlTKAlbSZzXnDFXnwXTVc_hHiqSlUiNzF9TBMZMTq3gzrbj4wfKg9Xsok6T8YQnhObGieLr16pCfWGvfyJ8LdXD-9iua0eHIHmTo7ktZK7MuBYrgQkF4tueJhpmDoCTmJ_o73xBkDNxq8fS8PB2Yj6ouHEVUOytEG_mKaYZDNouK643nolRiN_rG5UHMgV2iw1LHOJuAAc4i-JDE-acVmPP7alCMH8zEpMkW9USmUDkKsRBhzXc87t0iC49gjVlFfFCCMIRga6vzeCNtytlNH7UPTBqbtsW8N4nP8vrJVmw2T-1J4xGVYmFuL2E_9hIje-TOebjh_3XsXHenukdn45jn5zhH-fchgvB2wz5RZTZozC9oxRoX-cFDlczD_BdKtEUf9dIwlX5yBM')

try:
    response = api.get_profiles()
    if response['data']:
        profile_id = response['data'][-1]['id']
        if profile_id:
            api.delete_profiles([profile_id])

    fingerprint = []
    while not fingerprint:
        fingerprint = api.generate_fingerprint(platform='windows', browser_version=f'{random.randint(114, STABLE_CHROME_VERSION)}')

    data = api.fingerprint_to_profile(name='my superprofile', fingerprint=fingerprint)
    profile_id = api.create_profile(data)['browserProfileId']

    response = dolphin.run_profile(profile_id)
    
    if 'automation' in response and 'port' in response['automation']:
        port = response['automation']['port']
        driver = dolphin.get_driver(port=port)
        driver.get('https://google.com/')
        print(driver.title)
        driver.quit()
    else:
        print("Ошибка: Не удалось получить порт для автоматизации.")

except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    dolphin.close_profile(profile_id)
