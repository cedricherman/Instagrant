from bs4 import BeautifulSoup
import glob
import json
import multiprocessing
import os
import requests
import time
import warnings


def extract_permalink(json_file_api):
    """
        Collect permalinks from input json
        Returns a list of permalinks
    """
    # read json file
    with open(json_file_api) as f:
        year = json.load(f)

    # extract awards permalinks
    award_links = [y.get('link') for y in year]

    return award_links

def get_agency_branch(imp_info):
    """
        Extract agency name and branch name from html and returns it
        Input argument (imp_info) is a BeautifulSoup subtree
    """
    # Agency and Branch
    top_info = imp_info.findAll('div', class_ = 'col-md-6', limit=5)

    agency_branch = [ (i.find('span', class_='open-label').text.strip(':'),
                       i.find('span', class_='open-description').text)
                      for i in top_info]

    return agency_branch


def get_usd_others(imp_info):
    """
        Extract fields under Award Information (sollicitation field, dollar amount,...)
        Returns list of tuple (label, value)
    """
    # solicitation, award amount, ...
    mid_info = imp_info.findAll('div', class_ = 'col-md-3', limit=9)

    # loop through each field
    usd_others = [ (i.find('span', class_='open-label').text.strip(':'),
                    i.find('span', class_='open-description').text)
                    for i in mid_info]

    return usd_others


def get_people_info(imp_info):
    """
        Collect Principal Investigator, Business Contact Information and Research Institution
        Returns a list of tuples (field, value)
    """
    # list of people's information
    people_list = []

    # Principal Investigator
    people_info = imp_info.find('div', class_='col-md-4')
    pi = people_info.find('div', class_='award-sub')
    pi_d = pi.find_all_next('span', class_='award-node-section-label', limit=4)
    pi_info = dict([(i.text.strip(':'), i.next_sibling.strip('\xa0').replace('\xa0', ' ')) for i in pi_d])
    people_list.append( (pi.text, pi_info) )

    # Business Contact
    contact = people_info.find_next_sibling('div')
    contact_sub = contact.find('div', class_='award-sub')

    try:
        # here name of Business Contact has a tag and the rest does not
        name_str = contact_sub.find_next('span', class_='award-node-section-label')
        contact_info = {}
        contact_info[name_str.text.strip(':')] = name_str.next_sibling.strip('\xa0').replace('\xa0', ' ')
        contact_rest = [ i.replace('\xa0', '').split(':')  for i in name_str.next_siblings if isinstance(i,str) and ':' in i]
        contact_info.update(dict(contact_rest))
    except:
        # here there is no tags for each Business contact attribute (name, email,...)
        name_str = contact_sub.find_next('div', class_='award-sub-description')
        contact_rest = [ i.replace('\xa0', '').strip().split(':')  for i in name_str.contents if isinstance(i,str) and ':' in i]
        contact_info = dict(contact_rest)
        people_list.append( (contact_sub.text, contact_info) )

    # grab research institution
    inst = contact.find_next_sibling('div')
    inst_key = inst.find('div', class_='award-sub')
    ri = inst.select_one('div[class=award-sub-description] > div').text.strip()
    people_list.append( (inst_key.text, ri) )

    return people_list

def scrape_awards(json_file_api):
    """
        Scrape awards. Permalinks are available in json file specified in input argument
        Return a list of dictionaries, one dictionary per award information (abstract, USD, ...)
    """

    # recover file name only
    this_file = os.path.basename(json_file_api)
    print('Scraping awards reference {}'.format(this_file))

    # collect list of permalinks
    award_links = extract_permalink(json_file_api)

    # list of award data (dictionary)
    main_data = []

    # loop through each permalink
    for link in award_links:

        # scrape web page
        r = requests.get(link)

        # check response was good
        if r.status_code == 200:

            # use BeautifulSoup to structure html tags
            input_soup = BeautifulSoup(r.content, 'html5lib')

            # list of information (tuples of information)
            info_list = []

            try:
                # grab title
                title = input_soup.title.text.split('|')[0]
                info_list.append( ('title', title) )

                # relevant information are below this class
                imp_info = input_soup.find('div', class_= "award-info-wrapper")

                # get agency and associated branch
                agency_branch = get_agency_branch(imp_info)
                # agency_branch is a list of tuples, add each tuple to our info list
                info_list.extend(agency_branch)

                # get dollar amount and all other info under Award Information (see web page)
                usd_others = get_usd_others(imp_info)
                info_list.extend(usd_others)

                # Company info (Name and Address)
                info_list.append( ('company name', imp_info.find('div', class_='sbc-name-wrapper').text.strip() ) )
                info_list.append( ('company address', imp_info.find('div', class_= 'sbc-address-wrapper').text.strip() ) )

                # DUNS (company unique identifier)
                duns = imp_info.find('div', class_ = 'col-md-12')
                info_list.append( (duns.find('span', class_='open-label').text.strip(':'),
                                   duns.find('span', class_='open-description').text) )

                # collect contact information on Principal Investgator, Business Contact and Research Institution
                peoples = get_people_info(imp_info)
                info_list.extend( peoples )

                # grab abstract
                key = imp_info.select_one('div[class=abstract-wrapper] > div[class=info-wrapper]')
                abs_text = key.next_sibling.strip()
                info_list.append( (key.text, abs_text) )

                # convert list of tuples to dictionary and add it to our main list
                main_data.append(dict(info_list))

            # Something went wrong along the way
            except:
                warnings.warn('Scraping failed for {} at {}'.format(this_file, link), UserWarning)
                # keep track of permalink where html tree parsing had an error
                with open('tag_failed_links.txt', "a") as fplog:
                    fplog.write(''.join([link,'\n']))

        # response was not 200
        else:
            warnings.warn('Request failed for {} at {}'.format(this_file, link), UserWarning)
            # keep track of permalink where html tree parsing had an error
            with open('request_failed_links.txt', "a") as fpr:
                fpr.write(''.join([link,'\n']))

    print('Last award processed for {}'.format(this_file))

    # save whole year data to json immediately
    sbir_output = os.path.join(os.pardir,'data', 'interim', this_file)
    # save list of dictionaries to json file for that year
    with open(sbir_output, "w") as f:
        json.dump(main_data, f)


if __name__ == "__main__":
    # get start time of timer for processing time
    start_time = time.time()

    # number of processes (quad cores have 8 CPU, 1 CPU = 1 process at most)
    # Usually leave one process unused to be able to use your computer
    NUM_PROCESS = 7

    # list all json files in raw data folder
    json_list = glob.glob(os.path.join(os.pardir, 'data', 'raw', '*.json'))

    # list all json files in interim folder (already processed)
    json_list_done = glob.glob(os.path.join(os.pardir, 'data', 'interim', '*.json'))
    # only keep file name (e.g. remove path)
    json_list_done = [os.path.basename(k)  for k in json_list_done]

    # only keep non-processed json files
    json_list = [ fullpath for fullpath in json_list if os.path.basename(fullpath) not in json_list_done]

    # create pool
    with multiprocessing.Pool(processes=NUM_PROCESS, maxtasksperchild=None) as pool:

        # feed pool with all files from current year by partition
        pool.map(scrape_awards, json_list)

    # closing print statement
    print("--- %s seconds ---" % (time.time() - start_time))
