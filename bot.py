import telebot
from telebot import types
import re
import requests
from bs4 import BeautifulSoup
import hashlib

bot = telebot.TeleBot('6941144736:AAH2ZqgaijpXSUMDEtXLKvqDGFfDFjYIfw8')

@bot.message_handler(commands=['start'])
def send_welcome(message):
   bot.send_message(message.chat.id, "<b>Проверьте почту быстро!</b>\n\nПросто отправьте нужную почту боту", parse_mode='HTML')



@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    text = message.text.strip()
    user = message.chat.id
    if re.match(r'^[\w\.-]+@[\w\.-]+$', text):
        phones = ""#телефоны
        names = ""#имена
        reg = ""#регистрации
        my_world = ""#мой мир 
        adr = ""#адреса/местоположения
        birt = ""#дата рождения
        photos = []
        gravatar = ""

        icq = ""#профиль icq
        ok_ru = ""#поиск профиля в ок ру

        mesq = bot.send_message(user, "⏳<b>Ожидайте, ваш запрос обрабатывается</b>", parse_mode='HTML')
        mlogin = text.split("@")[0]#извлекаем логин
        domain = text.split("@")[1]#извлекаем домен
        
        ###маил ру###
        url_api_mail_ru = f'https://account.mail.ru/api/v1/user/password/restore?email={mlogin}@{domain}'
        response_mail = requests.get(url_api_mail_ru)

        if response_mail.status_code == 200:
            data = response_mail.json()
    
            phone = None
            if "body" in data and "phones" in data["body"]:
                phone_list = data["body"]["phones"]
                if len(phone_list) > 0:
                    phone = phone_list[0]
            if phone != None:
                phones += "<code>"  + phone + "</code>"  + " ,"#записываем найденый телефон

        ###ссылки на профили в мой мир###
        if domain == "mail.ru":
            my_world += f"https://my.mail.ru/mail.ru/{mlogin}/"
        if domain == "list.ru":
            my_world += f"https://my.mail.ru/list.ru/{mlogin}/"
        if domain == "bk.ru":
            my_world += f"https://my.mail.ru/bk.ru/{mlogin}/"
        if domain == "inbox.ru":
            my_world += f"https://my.mail.ru/inbox.ru/{mlogin}/"
        if domain == "internet.ru":
            my_world += f"https://my.mail.ru/internet.ru/{mlogin}/"
        
        if my_world != "":
            url_my_world = my_world
            response_world = requests.get(url_my_world)

            if response_world.status_code == 200:
                response_world.encoding = 'utf-8' 
                html_content = response_world.text
                 
                soup = BeautifulSoup(html_content, 'html.parser')
                location_element = soup.find('span', itemprop='name')

                if location_element:
                    location = location_element.text.strip()
                    if location:
                        adr += "\n" + "<code>" + location + "</code>"#местоположение

                name_tag = soup.find('h1', itemprop='name')
                if name_tag:
                    name = name_tag.get_text(separator=" ").strip()
                    names += "<i>" + name + "</i>" + " ,"#имя
          
                birthdate_span = soup.find('span', class_='b-right-column__block__anketa__item__body__text', itemprop='birthDate')

                if birthdate_span:
                    birthdate = birthdate_span.get_text(separator=" ").strip()
                    birt += "<code>" + birthdate + "</code>" + " ,"#дата рождения

    

        ###OK.RU###
        masked_name = ''
        masked_email = ''
        masked_phone = ''
        profile_info = ''
        pr_gorod = ''
        session = requests.Session()
        session.get(
                f'https://www.ok.ru/dk?st.cmd=anonymMain&st.accRecovery=on&st.error=errors.password.wrong&st.email={mlogin}@{domain}')
        request = session.get(
                f'https://www.ok.ru/dk?st.cmd=anonymRecoveryAfterFailedLogin&st._aid=LeftColumn_Login_ForgotPassword')
        root_soup = BeautifulSoup(request.content, 'html.parser')
        soup = root_soup.find('div', {'data-l': 'registrationContainer,offer_contact_rest'})
        if soup:
            account_info = soup.find('div', {'class': 'ext-registration_tx taCenter'})
            masked_email = soup.find('button', {'data-l': 't,email'})
            masked_phone = soup.find('button', {'data-l': 't,phone'})
            if masked_phone:
                masked_phone = masked_phone.find('div', {'class': 'ext-registration_stub_small_header'}).get_text()
            if masked_email:
                masked_email = masked_email.find('div', {'class': 'ext-registration_stub_small_header'}).get_text()
            else:
                masked_email = ''
            if account_info:
                masked_name = account_info.find('div', {'class': 'ext-registration_username_header'})
                if masked_name:
                    masked_name = masked_name.get_text()
                account_info = account_info.findAll('div', {'class': 'lstp-t'})
                if account_info:
                    profile_info = account_info[0].get_text()
                    profile_registred = account_info[1].get_text()
                else:
                    profile_info = None
                    profile_registred = None
            else:
                pass
        if profile_info != "":
           pr_inf = profile_info.split(', ')
           if len(pr_inf) == 2:
                pr_age = pr_inf[0]
                pr_gorod = pr_inf[1]
                if pr_age != "":
                   pp = pr_age.split()
                   if len(pp) == 2:
                       tttt = pp[0]
                       h = 2024 - int(tttt) 
                       birt += "<code>" + str(h) + " год" + "</code> ,"
                if pr_gorod:
                    adr += "\n" + "<code>" + pr_gorod + "</code>"
        if masked_phone != "" or None:
            if masked_phone != None:
                 phones += "<code>" + masked_phone + "</code>" + " ,"
        if masked_name != "" or None:
            naming = masked_name.replace("*", "")
            names += "<i>" + naming + "</i>" + " ,"
            reg += "<code>OK.RU</code> ,"
            if pr_gorod:
                if naming:
                    if pr_age:
                       ok_ru += f"https://m.ok.ru/dk?st.cmd=anonymUsersOnlySearchV2&st.university=&st.gn=&st.ageF=&st.cityId=&st.single=false&st.search={pr_gorod} {naming} {pr_age}&st.school=&st.ageT=&st.online=false&_prevCmd=anonymUsersOnlySearchV2&tkn=8395&_searchToolbarMode=false&_searchFieldId=AnonymUsersOnlySearchFormV2Field&_searchQueryType=0"

        ###ICQ###
        url_icq = f'https://icq.im/{mlogin}@{domain}'  # замените на фактический URL

        headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    }

        response_i = requests.get(url_icq, headers=headers)

        if response_i.status_code == 200:

            html_content = response_i.content


            soup_i = BeautifulSoup(html_content, 'html.parser')


            profile_name = soup_i.find('h2', class_='icq-profile__name')

 
            if profile_name:
                name = profile_name.get_text(strip=True)
                names += "<i>" + name + "</i>" + " ,"
                reg += f"<code>ICQ</code> ,"
                icq += f"https://icq.im/{mlogin}@{domain}"

                URLicq = icq
                HEADERS = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
                }
                raq = requests.get(URLicq, headers=HEADERS)
                soup = BeautifulSoup(raq.content, 'html.parser')
                items = soup.findAll('div', class_='icq-profile__avatar')
                icq_url = None
                for item in items:
                    style_attr = item.get('style')
                    if style_attr:
                        match = re.search(r"url\('([^']+)'\)", style_attr)
                        if match:
                            icq_url = match.group(1)
                            if "profile_dummy" in icq_url:
                                icq_url = "https://icq.im/" + icq_url
                            photos.append(icq_url)

                            break


        emailtohash = f"{mlogin}@{domain}"
        hashed_name = hashlib.md5(emailtohash.encode()).hexdigest()
        rhash = requests.get(f'https://gravatar.com/{hashed_name}.json')
        data = rhash.json()
        if data != "User not found": 
            GravatarFullName = data['entry'][0]['displayName']
            if rhash.status_code == 200:
                names += f"<i>{GravatarFullName}</i> ,"
                gravatar += f"https://gravatar.com/{GravatarFullName}"
                reg += "<code>gravatar</code> ,"
                url = gravatar  # замените на фактический URL

# Выполняем GET-запрос для получения HTML-кода страницы
                response_g = requests.get(url)

# Проверяем успешность запроса
                if response_g.status_code == 200:
    # Получаем HTML-код страницы
                    html_contentg = response_g.content

    # Создаем объект BeautifulSoup для парсинга HTML
                    soupg = BeautifulSoup(html_contentg, 'html.parser')

    # Ищем элемент img с классом g-profile__profile-image
                    profile_image_element = soupg.find('img', class_='g-profile__profile-image')

    # Проверяем, что элемент найден
                    if profile_image_element:
                        profile_image_url = profile_image_element['src']
                        photos.append(profile_image_url)
               
                


        otchet = ""
        otchet += f"""
📪
├ Логин: <code>{mlogin}</code>
└ Домен: <code>{domain}</code>
"""
        
        if names != "":
            n = names[:-1]
            otchet += f"""
📓 <b>Возможные имена:</b>
└ {n}
"""
        if birt != "":
            b = birt[:-1]
            otchet += f"""
🏥 <b>Дата рождения:</b> {b}"""
        
        if phones != "":
            p = phones[:-1]
            otchet += f"""
📪 <b>Телефон:</b> {p}"""
            
        if adr != "":
            otchet += f"""
🏠 <b>Возможные адреса:</b>{adr}
"""
            
        if reg != "":
            r = reg[:-1]
            otchet += f"""
🌐 <b>Регестрции:</b> {r}"""

        f = mesq.message_id
        bot.delete_message(user, f)
        r = types.InlineKeyboardMarkup()
        if icq != "":
           r.add(types.InlineKeyboardButton('Профиль ICQ', url=icq))
        if ok_ru != "":
            r.add(types.InlineKeyboardButton('Поиск OK.RU', url=ok_ru))
        if gravatar != "":
            r.add(types.InlineKeyboardButton('Профиль Gravatar', url=gravatar))

        if photos != []:
            media = [types.InputMediaPhoto(media=url) for url in photos]
            bot.send_media_group(chat_id=message.chat.id, media=media)

                
        
        bot.send_message(user, otchet, reply_markup=r, parse_mode='HTML')


bot.polling()