#  copied from https://github.com/amckenna41/pyWikiCommons

import requests
import argparse
import logging
import os, getpass
from urllib.parse import unquote
from props import ALL_PROPS, IMAGEINFO_IIPROPS, FORMAT, ACTIONS

#initialise logger module
log = logging.getLogger("WikiCommons")

#set header info for requests module
USER_AGENT_HEADER = {'User-Agent': 'pyWikiCommons/{} ({}; {})'.format('1',
                                       'https://github.com/amckenna41/pyWikiCommons', getpass.getuser())}
#wikimedia API URL
# BASE_URL = "https://commons.wikimedia.org/w/api.php?action=query"
BASE_URL = "https://en.wikipedia.org/w/api.php?action="

def download_commons_image(filename, outputFolder="wikiCommonsOutput", output_file_name="", action="query", format_='json',
    props=['imageinfo'], iiprops=["url"], decode=True):
    """
    Download image, specified by filename, using the Wikimedia API.

    Parameters
    ----------
    :filename (str):
        name of image to download
    :outputFolder (str):
        path of output folder where image is stored
    :output_file_name (str):
        custom name for the output file
    :format_ (str):
        format of API call response, can be json, xml or yaml; JSON used by default.
    :props (array):
        list of properties to return from API call about image, "imageinfo" property
        required by default to obtain URL of image. Full list of properties available
        in the ALL_PROPS variable in props.py .
    :iiprops (array):
        list of available iiprops is dependant on selected property. The iiprops array
        is a list of sub-level properties returned from API call. "url" iiprop required
        by defauly to obtain URL of image. Full list of properties are available in props.py .
    :decode (bool):
        whether to decode unicode string of image filename when saving.

    Returns
    -------
    None
    """
    valid_props = []
    valid_iiprops = []

    #iterate over all input properties, validating their correctness
    for prop in props:
      if (prop not in ALL_PROPS):
        print('Input property not in available props {}').format(prop)
      else:
        valid_props.append(prop)

    #ensure imageinfo property in array
    if ("imageinfo" not in valid_props):
        valid_props.append("imageinfo")

    #ensure selected action is valid, if not set to "query"
    if (action not in ACTIONS):
        action="query"

    #iterate over all input ii properties, validating their correctness
    for iiprop in iiprops:
      if (iiprop not in IMAGEINFO_IIPROPS):
        print('Input iiproperty not in available iiprops {}').format(iiprop)
      else:
        valid_iiprops.append(iiprop)

    #ensure url iiproperty in array
    if ("url" not in valid_iiprops):
        valid_iiprops.append("url")

    #if invalid format input then use json by default
    if (format_ not in FORMAT):
      format_ = "json"

    #ensure filename is prefixed with "File:" to work with API
    if (filename[:5] != "File:"):
      filename = "File:" + filename

    #build request url with all query parameters
    request_url = BASE_URL + action + "&format=" + format_ + "&titles=" + filename
    request_url += "&prop=" + '|'.join(valid_props)
    request_url += "&iiprop=" + '|'.join(valid_iiprops)

    #generate API call, convert to json
    response = requests.get(request_url, headers=USER_AGENT_HEADER).json()

    #get download URL for image
    file_url = response['query']['pages'].popitem()[1]['imageinfo'][0]['url']

    #generate call to image url
    new_response = requests.get(file_url, stream=True, headers=USER_AGENT_HEADER)

    #create output folder
    if not (os.path.isdir(outputFolder)):
        os.mkdir(outputFolder)

    #decode any unicode characters
    if (decode):
      filename = unquote(filename)

    #remove any leading or trailing whitespace
    filename = filename.strip()

    #remove the file string from filename
    if (filename[:5] == "File/"):
      filename = filename[5:]

    #create file
    # file = open(os.path.join(outputFolder, filename), "wb")
    file = open(os.path.join(outputFolder, output_file_name + '.jpg'), "wb")

    #write image to file
    file.write(new_response.content)

    #close file
    file.close()

    print(f'File ({filename}) successfully saved to output folder /{outputFolder}')

def get_commons_url(filename, action="query", format_="json"):
  """
  Get the download url of image from Wikimedia API call.

  Parameters
  ----------
  :filename (str):
    name of image to download
  :format_ (str):
    format of API call response, can be json, xml or yaml; JSON used by default.

  Returns
  -------
  :file_url (str):
    download url for filename on Wikimedia.

  """
  #build url and make API call, convert output to json format
  request_url = BASE_URL + action + "&format=" + format_ + "&titles=" + filename + "&prop=imageinfo&iiprop=url"
  response = requests.get(request_url).json()

  #parse API response to get the download url of file
  file_url = response['query']['pages'].popitem()[1]['imageinfo'][0]['url']

  return file_url