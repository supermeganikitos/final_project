import json
import math
import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
import requests

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


def get_span(coords_1, coords_2):
    l, b = coords_1.split(" ")
    r, t = coords_2.split(" ")
    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) * 1.1
    dy = abs(float(t) - float(b)) * 1.1
    # Собираем размеры в параметр span
    span = f"{dx},{dy}"
    return span


def make_static_maps_response(someval_, delta_, map_or_sat, users_pt_s=False):
    global someval, pt_s
    someval = list(map(float, someval_))
    delta_ = str(delta_)
    map_params = {
        "ll": ",".join((str(someval_[0]), str(someval_[1]))),
        "spn": ",".join([delta_, delta_]),
        "l": map_or_sat
    }
    if users_pt_s:
        map_params['pt'] = users_pt_s
    else:
        if pt_s:
            map_params['pt'] = '~'.join((','.join(i) for i in pt_s))
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)
    map_file = "map.jpg"
    with open(map_file, "wb") as file:
        file.write(response.content)
    return map_file


def blit_amg(map_fil):
    scr1 = pygame.image.load(map_fil)
    screen.blit(scr1, (0, 100))


someval = [37.617698, 55.755864]
pt_s = []
delta = 0.2
map_sat_hyb = 'map'
map_file = make_static_maps_response(someval, delta, map_sat_hyb)
pygame.init()
pygame.display.set_caption('Карта')
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
text_resp_adress = TextBox(screen, 0, 50, 500, 50)
text_resp_org = TextBox(screen, 0, 0, 500, 50)
text_adress = TextBox(screen, 0, 550, 600, 50)


def func():
    global delta
    map_params = {
        'apikey': API_KEY,
        "geocode": ''.join(text_resp_adress.text),
        "lang": 'ru_RU',
        "format": "json"
    }
    map_api_server = 'http://geocode-maps.yandex.ru/1.x/'
    response = requests.get(map_api_server, params=map_params)
    if response:
        try:
            json_response = response.json()
            with open('js.json', 'w') as f:
                json.dump(json_response, f, indent=4)
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            adress = toponym['metaDataProperty']['GeocoderMetaData']["AddressDetails"]["Country"]["AddressLine"]
            text_adress.setText(adress)
            toponym_coodrinates = toponym["Point"]["pos"].split()
            if text_resp_org.getText().strip():
                toponym_longitude, toponym_lattitude = toponym_coodrinates
                search_api_server = "https://search-maps.yandex.ru/v1/"
                api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
                address_ll = f"{toponym_longitude},{toponym_lattitude}"
                search_params = {
                    "apikey": api_key,
                    "text": text_resp_org.getText(),
                    "lang": "ru_RU",
                    "ll": address_ll,
                    "type": "biz"
                }

                response2 = requests.get(search_api_server, params=search_params)
                if not response2:
                    print("Ошибка выполнения запроса:")
                    print(response)
                    print("Http статус:", response.status_code, "(", response.reason, ")")
                # Преобразуем ответ в json-объект
                json_response = response2.json()
                with open('scoring.json', 'w', encoding='UTF-8') as f:
                    json.dump(json_response, f, indent=4)
                organization = json_response["features"][0]
                org_name = organization["properties"]["CompanyMetaData"]["name"]
                org_address = organization["properties"]["CompanyMetaData"]["address"]
                org_intervals = organization["properties"]["CompanyMetaData"]["Hours"]["Availabilities"][0]

                if 'TwentyFourHours' in org_intervals.keys() and org_intervals['TwentyFourHours']:
                    org_hours = 'Круглосуточная'
                else:
                    org_hours_from = \
                    organization["properties"]["CompanyMetaData"]["Hours"]["Availabilities"][0]["Intervals"][0]["from"]
                    org_hours_to = organization["properties"]["CompanyMetaData"]["Hours"]["Availabilities"][0]["Intervals"][0][
                        "to"]
                    org_hours = f'{org_hours_from} - {org_hours_to}'
                point = organization["geometry"]["coordinates"]
                org_point = "{0} {1}".format(point[0], point[1])
                delta = get_span(org_point, ' '.join([toponym_longitude, toponym_lattitude]))
                print("Имя: " + org_name)
                print("Адрес: " + org_address)
                print("Часы работы: " + org_hours)
                print("Расстояние: "
                      + str(round(lonlat_distance((float(toponym_longitude), float(toponym_lattitude)),
                                                  (float(point[0]), float(point[1]))))))


                map_params = [[str((float(toponym_longitude) + float(point[0])) / 2), str((float(toponym_lattitude) + float(point[1])) / 2)], delta,
                    map_sat_hyb,
                    ",".join([toponym_longitude, toponym_lattitude]) +
                          ',ya_ru' + '~' + ",".join([str(point[0]), str(point[1])]) + ',org'
                    ]
                pt_s.append(toponym_coodrinates)
                map_file_ = make_static_maps_response(*map_params)
                blit_amg(map_file_)
            else:
                json_response = response.json()
                with open('js.json', 'w') as f:
                    json.dump(json_response, f, indent=4)
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                adress = toponym['metaDataProperty']['GeocoderMetaData']["AddressDetails"]["Country"]["AddressLine"]
                text_adress.setText(adress)
                print(adress)
                toponym_coodrinates = toponym["Point"]["pos"].split()
                pt_s.append(toponym_coodrinates)
                map_file_ = make_static_maps_response(toponym_coodrinates, delta, map_sat_hyb)
                blit_amg(map_file_)
        except IndexError as ind_err:
            print("Ошибка выполнения запроса: попытайтесь найти что нибудь другое.")
    else:
        print("Ошибка выполнения запроса:")
        print(response)
        print("Http статус:", response.status_code, "(", response.reason, ")")


def clear_func():
    pt_s.clear()
    text_adress.setText('')
    map_file = make_static_maps_response(someval, delta, map_sat_hyb)
    blit_amg(map_file)


button_search_adress = Button(screen, 500, 0, 50, 100, text='Искать', onClick=func, fontSize=15)
button_click = Button(screen, 550, 0, 50, 100, text='Очистить', onClick=clear_func, fontSize=15)
blit_amg(map_file)


if __name__ == '__main__':
    pygame.display.flip()
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    if 0.2 <= delta:
                        delta -= 0.05
                        map_file = make_static_maps_response(someval, delta, map_sat_hyb)
                        blit_amg(map_file)
                if event.key == pygame.K_PAGEDOWN:
                    if delta <= 20:
                        delta += 0.05
                        map_file = make_static_maps_response(someval, delta, map_sat_hyb)
                        blit_amg(map_file)
                if event.key == pygame.K_UP:
                    someval[1] += delta * 2
                    map_file = make_static_maps_response(someval, delta, map_sat_hyb)
                    blit_amg(map_file)
                if event.key == pygame.K_DOWN:
                    someval[1] -= delta * 2
                    map_file = make_static_maps_response(someval, delta, map_sat_hyb)
                    blit_amg(map_file)
                if event.key == pygame.K_LEFT:
                    someval[0] -= delta * 2
                    map_file = make_static_maps_response(someval, delta, map_sat_hyb)
                    blit_amg(map_file)
                if event.key == pygame.K_RIGHT:
                    someval[0] += delta * 2
                    map_file = make_static_maps_response(someval, delta, map_sat_hyb)
                    blit_amg(map_file)
                if event.key == pygame.K_F1:
                    map_sat_hyb = 'map'
                    map_file = make_static_maps_response(someval, delta, map_sat_hyb)
                    blit_amg(map_file)
                if event.key == pygame.K_F2:
                    map_sat_hyb = 'sat'
                    map_file = make_static_maps_response(someval, delta, map_sat_hyb)
                    blit_amg(map_file)
                if event.key == pygame.K_q:
                    clear_func()
        try:
            pygame_widgets.update(events)
        except pygame.error as undef_err:
            print(undef_err.__str__())
        pygame.display.flip()
    pygame.quit()