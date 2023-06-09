import easyimap, json, os, re, requests
from datetime import datetime, timedelta
from urllib.parse import unquote

check_list = {
  'UCJFZiqLMntJufDCHc6bQixg': 'ホロライブ',
  'UCp6993wxpyDPHUpavwDFqgg': 'ときのそら',
  'UCDqI2jOz0weumE8s7paEk6g': 'ロボ子さん',
  'UC5CwaMl1eIgY8h02uZw7u8A': '星街すいせい',
  'UC-hM6YJuNYVAmUWxeIr9FeA': 'さくらみこ',
  'UC0TXe_LYZ4scaW2XMyi5_kw': 'AZKi',
  'UCD8HOxPs4Xvsm8H0ZxXGiBw': '夜空メル',
  'UCdn5BQ06XqgXoAxIhbqw5Rg': '白上フブキ',
  'UCQ0UDLQCjY0rmuxCDE38FGg': '夏色まつり',
  'UCFTLzh12_nrtzqBPsTCqenA': 'アキ・ローゼンタール',
  'UC1CfXB_kRs3C-zaeTG3oGyg': '赤井はあと',
  'UC1opHUrw8rvnsadT-iGp7Cg': '湊あくあ',
  'UCXTpFs_3PqI41qX2d9tL2Rw': '紫咲シオン',
  'UC7fk0CB07ly8oSl0aqKkqFg': '百鬼あやめ',
  'UC1suqwovbL1kzsoaZgFZLKg': '癒月ちょこ',
  'UCvzGlP9oQwU--Y0r9id_jnA': '大空スバル',
  'UCp-5t9SrOQwXMU7iIjQfARg': '大神ミオ',
  'UCvaTdHTWBGv3MKj3KVqJVCw': '猫又おかゆ',
  'UChAnqc_AY5_I3Px5dig3X1Q': '戌神ころね',
  'UC1DCedRgGHBdm81E1llLhOQ': '兎田ぺこら',
  'UCl_gCybOJRIgOXw6Qb4qJzQ': '潤羽るしあ',
  'UCvInZx9h3jC2JzsIzoOebWg': '不知火フレア',
  'UCdyqAaZDKHXg4Ahi7VENThQ': '白銀ノエル',
  'UCCzUftO8KOVkV4wQG1vkUvg': '宝鐘マリン',
  'UCZlDXzGoo7d44bwdNObFacg': '天音かなた',
  'UCS9uQI-jC3DE0L4IpXyvr6w': '桐生ココ',
  'UCqm3BQLlJfvkTsX_hvm0UmA': '角巻わため',
  'UC1uv2Oq6kNxgATlCiez59hw': '常闇トワ',
  'UCa9Y57gfeY0Zro_noHRVrnw': '姫森ルーナ',
  'UCFKOVgVbGmX65RxO3EtH3iw': '雪花ラミィ',
  'UCAWSyEs_Io8MtpY3m-zqILA': '桃鈴ねね',
  'UCUKD-uaobj9jiqB-VXt71mA': '獅白ぼたん',
  'UCK9V2B22uJYu3N7eR_BT9QA': '尾丸ポルカ',
  'UCENwRMx5Yh42zWpzURebzTw': 'ラプラス・ダークネス',
  'UCs9_O1tRPMQTHQ-N_L6FU2g': '鷹嶺ルイ',
  'UC6eWCld0KwmyHFbAqK3V-Rw': '博衣こより',
  'UCIBY1ollUsauvVi4hW4cumw': '沙花叉クロヱ',
  'UC_vMYWcDjmfdpH6r4TTn1MQ': '風真いろは',
  'UCOyYb1c43VlX9rc_lT6NKQw': 'Ayunda Risu',
  'UCP0BspO_AMEe3aQqqpo89Dg': 'Moona Hoshinova',
  'UCAoy6rzhSf4ydcYjJw3WoVg': 'Airani Iofifteen',
  'UCYz_5n-uDuChHtLo7My1HnQ': 'Kureiji Ollie',
  'UC727SQYUvx5pDDGQpTICNWg': 'Anya Melfissa',
  'UChgTyjG-pdNvxxhdsXfHQ5Q': 'Pavolia Reine',
  'UCTvHWSfBZgtxE4sILOaurIQ': 'Vestia Zeta',
  'UCZLZ8Jjx_RN2CXloOmgTHVg': 'Kaela Kovalskia',
  'UCjLEmnpCNeisMxy134KPwWw': 'Kobo Kanaeru',
  'UCL_qhgtOy0dy1Agp8vkySQg': 'Mori Calliope',
  'UCHsx4Hqa-1ORjQTh9TYDhww': 'Takanashi Kiara',
  'UCMwGHR0BTZuLsmjY_NT5Pwg': 'Ninomae Ina\'nis',
  'UCoSrY_IQQVpmIRZ9Xf-y93g': 'Gawr Gura',
  'UCyl1z3jo3XHR1riLFKG5UAg': 'Watson Amelia',
  'UCsUj0dszADCGbF3gNrQEuSQ': 'Tsukumo Sana',
  'UCO_aKKYxn4tvrqPjcTzZ6EQ': 'Ceres Fauna',
  'UCmbs8T6MWqUHP1tIQvSgKrg': 'Ouro Kronii',
  'UC3n5uGu18FoCy23ggWWp8tA': 'Nanashi Mumei',
  'UCgmPnx-EEeOrZSg5Tiw7ZRQ': 'Hakos Baelz',
  'UC8rcEBzJSleTkf_-agPM20g': 'IRyS',
  'UCWCc8tO-uUl_7SJXIKJACMw': '神楽めあ',
  'UC8NZiqKx6fsDT3AVcMiVFyA': '犬山たまき',
  'UC9V3Y3_uzU5e-usObb6IE1w': '星川サラ'
}

class Channel:
  def __init__(self, _id: str, **kwargs) -> None:
    self._id = _id
    self.url = f'https://www.youtube.com/channel/{self._id}'
    for attr, value in kwargs.items():
      setattr(self, attr, value)

class Playlist:
  def __init__(self, _id: str, **kwargs) -> None:
    self._id = _id
    self.url = f'https://www.youtube.com/playlist?list={self._id}'
    for attr, value in kwargs.items():
      setattr(self, attr, value)

class Video:
  def __init__(self, _id: str, **kwargs) -> None:
    self._id = _id
    self.url = f'https://youtu.be/{self._id}'
    for attr, value in kwargs.items():
      setattr(self, attr, value)

class Comment:
  def __init__(self, _id: str, **kwargs) -> None:
    self._id = _id
    for attr, value in kwargs.items():
      setattr(self, attr, value)

class Post:
  def __init__(self, _id: str, **kwargs) -> None:
    self._id = _id
    self.url = f'https://www.youtube.com/post/{self._id}'
    for attr, value in kwargs.items():
      setattr(self, attr, value)

def str_to_date(date_string: str = None) -> datetime:
  if not date_string: return None
  return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')

def get_youtube_data(path: str) -> dict:
  key = os.getenv(f'YOUTUBE_API_KEY_{str(datetime.utcnow().hour//3+1)}')
  url = f'https://www.googleapis.com/youtube/v3/{path}&key={key}'
  data = requests.get(url).json()
  return data

def get_description(data: str, user: str = 'Else') -> str:
  separators = {'Aqua': '▷◁', 'Shion': '୨୧'}
  separator = separators.get(user)
  description = data.split(separator, 1)[0] if separator and separator in data else data
  description = description[:1000] + '...' if len(description) > 1000 else description
  return description

def get_length(data: dict) -> str:
  length = data['contentDetails']['duration']
  time_units = {'H': 'hours', 'M': 'minutes', 'S': 'seconds'}
  time_parts = re.findall(r'(\d+)([HMS])', length)
  time_dict = {time_units[unit]: int(value) for value, unit in time_parts}
  time_delta = timedelta(**time_dict)
  length = str(time_delta)
  return length

def get_thumbnail(data: dict) -> str:
  sizes = ['maxres', 'standard', 'high', 'medium', 'default']
  for size in sizes:
    if size in data:
      thumbnail = data[size]['url'].split('=s')[0].replace('_live', '')
      return thumbnail
  return os.getenv('DEFAULT_PICTURE')

def get_channel(channel_uid: str) -> Channel:
  path = f'channels?part=brandingSettings,snippet,statistics&id={channel_uid}'
  data = get_youtube_data(path)['items'][0]

  channel = Channel(
    _id = channel_uid,
    id = data['snippet']['customUrl'][1:],
    title = data['snippet']['title'],
    description = data['snippet'].get('description', 'None'),
    icon = get_thumbnail(data['snippet']['thumbnails']),
    banner = data['brandingSettings'].get('image', {}).get('bannerExternalUrl', os.getenv('DEFAULT_PICTURE')),
    subscriber = int(data['statistics']['subscriberCount']),
    view = int(data['statistics']['viewCount'])
  )
  return channel

def get_channelSection(channel_uid: str) -> list:
  section_list = []
  path = f'channelSections?part=contentDetails,snippet&channelId={channel_uid}'
  data = get_youtube_data(path)['items']
  for section in data:
    type = section['snippet']['type']
    if type == 'singleplaylist':
      content = section['contentDetails']['playlists'][0]
      section_list.append({'Type': type, 'Content': content})
    elif type == 'multipleplaylists':
      content = section['contentDetails']['playlists']
      section_list.append({'Type': type, 'Content': content})
    elif type == 'multiplechannels':
      content = section['contentDetails']['channels']
      section_list.append({'Type': type, 'Content': content})
    elif type == 'channelsectiontypeundefined': pass
    else: section_list.append({'Type': type})
  return section_list

def get_playlist(channel_uid: str) -> list:
  playlist_list = []
  path = f'playlists?part=snippet,status&channelId={channel_uid}&maxResults=50'
  data_list = get_youtube_data(path)['items']
  for data in data_list:
    playlist = Playlist(
      _id = data['id'],
      title = data['snippet']['title'],
      description = data['snippet'].get('description', 'None'),
      thumbnail = get_thumbnail(data['snippet']['thumbnails']),
      status = data['status']['privacyStatus'],
    )
    playlist_list.append(playlist)
  return playlist_list

def get_playlistItem(playlist_id: str, max: int = 50) -> list:
  video_list, page_token = [], ''
  while page_token != None:
    path = f'playlistItems?part=snippet&playlistId={playlist_id}&maxResults={max}&pageToken={page_token}'
    item_list = get_youtube_data(path)
    page_token = item_list.get('nextPageToken') if max == 50 else None

    for item in item_list['items']:
      video = Video(
        _id = item['snippet']['resourceId']['videoId'],
        title = item['snippet']['title'],
        thumbnail = get_thumbnail(item['snippet']['thumbnails'])
      )
      video_list.append(video)
  return video_list

def get_video_item(data: dict) -> Video:
  live_detail = data.get('liveStreamingDetails', {})
  video = Video(
    _id = data['id'],
    title = data['snippet']['title'],
    thumbnail = get_thumbnail(data['snippet']['thumbnails']),
    description = data['snippet'].get('description', 'None'),
    length = get_length(data),
    status = data['snippet']['liveBroadcastContent'],
    view = int(data['statistics']['viewCount']) if 'viewCount' in data['statistics'] else None,
    comment = 'commentCount' in data['statistics'],
    published_time = str_to_date(data['snippet']['publishedAt']),
    scheduled_time = str_to_date(live_detail.get('scheduledStartTime')),
    start_time = str_to_date(live_detail.get('actualStartTime')),
    end_time = str_to_date(live_detail.get('actualEndTime')),
    chat_id = live_detail.get('activeLiveChatId'),
    author = Channel(_id=data['snippet']['channelId'])
  )
  return video

def get_video(video_id: str) -> Video:
  path = f'videos?part=contentDetails,liveStreamingDetails,snippet,statistics,status&id={video_id}'
  data = get_youtube_data(path)['items']
  if data:
    video = get_video_item(data[0])
    return video
  return None

def get_videos(video_id_list: list) -> list:
  if video_id_list:
    video_ids = [','.join(video_id_list[i:i+50]) for i in range(0, len(video_id_list), 50)]
    video_list = []
    for video_id in video_ids:
      path = f'videos?part=contentDetails,liveStreamingDetails,snippet,statistics,status&id={video_id}'
      item_list = get_youtube_data(path)['items']
      for item in item_list:
        video = get_video_item(item)
        video_list.append(video)
    return video_list
  return []

def get_comment(id: str, type: str) -> list:
  comment_list, page_token = [], ''
  while page_token != None:
    path = f'commentThreads?part=snippet&allThreadsRelatedToChannelId={id}&maxResults=100&textFormat=plainText&pageToken={page_token}' if type == 'comment' else f'comments?part=snippet&parentId={id}&maxResults=100&textFormat=plainText&pageToken={page_token}'
    item_list = get_youtube_data(path)
    page_token = item_list.get('nextPageToken')

    for item in item_list['items']:
      data = item['snippet']['topLevelComment']['snippet'] if type == 'comment' else item['snippet']
      time = str_to_date(data['publishedAt'])
      author_uid = data.get('authorChannelId', {}).get('value')

      if time < datetime.utcnow() - timedelta(hours=1):
        page_token = None
        break
      elif author_uid in check_list:
        comment = Comment(
          _id = item['id'].split('.')[-1],
          time = time,
          text = data['textDisplay'],
          author = Channel(_id=author_uid, title=data['authorDisplayName'], icon=data['authorProfileImageUrl'].split('=s')[0])
        )
        if type == 'comment': comment.video = Video(_id=data['snippet']['videoId'])
        comment_list.append(comment)

  return comment_list

def get_post(channel_uid: str) -> list:
  url = f'https://www.youtube.com/channel/{channel_uid}/community'
  request = requests.get(url)
  data = json.loads(re.findall(r'ytInitialData = (.+);\s*<\/script>', request.text)[0])
  post_data = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][-4]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
  
  post_list = []
  for post in post_data[:-1]:
    post = post['backstagePostThreadRenderer']['post']['backstagePostRenderer']
    if 'backstageImageRenderer' in post['backstageAttachment']: post_image = [post['backstageAttachment']['backstageImageRenderer']['image']['thumbnails'][-1]['url'].split('=s')[0]]
    elif 'postMultiImageRenderer' in post['backstageAttachment']: post_image = [image['backstageImageRenderer']['image']['thumbnails'][-1]['url'].split('=s')[0] for image in post['backstageAttachment']['postMultiImageRenderer']['images']]
    else: post_image = []

    post_item = Post(
      _id = post['postId'],
      text = ''.join([run['text'] if 'http' not in run['text'] or '...' not in run['text'] else unquote(run['navigationEndpoint']['urlEndpoint']['url'].split('&q=')[-1]) if 'q=' in run['navigationEndpoint']['urlEndpoint']['url'] else run['navigationEndpoint']['urlEndpoint']['url'] for run in post['contentText']['runs']]),
      video = f'https://youtu.be/{post["backstageAttachment"]["videoRenderer"]["videoId"]}' if 'videoRenderer' in post['backstageAttachment'] else None,
      image = post_image
    )
    post_list.append(post_item)
  return post_list

def get_member_post(channel_title: str) -> list:
  post_list = []
  imapper = easyimap.connect('imap.gmail.com', os.getenv('MAIL_ACCOUNT'), os.getenv('MAIL_PASSWORD'))
  for mail_id in imapper.listids(limit=10):
    mail = imapper.mail(mail_id)
    if '頻道會員專屬內容' in mail.title and channel_title in mail.title:
      post_id = re.search(r'community\?feature=em-sponsor&lb=([\w-]+)', mail.body).group(1)
      match = re.search(r'(?:youtube\.com\/(?:watch\?v=|live\/)|youtu\.be\/)([\w-]{11})', mail.body)
      video_id = match.group(1) if match else None
      post_list.append((post_id, video_id))
  imapper.quit()
  return post_list

def get_collab() -> list:
  request = requests.get('https://schedule.hololive.tv/lives/hololive')
  video_id_list = re.findall(r'href="https:\/\/www\.youtube\.com\/watch\?v=([\w-]+)"', request.text)
  video_list = get_videos(video_id_list)
  return video_list

def get_link_item(item: dict, type: str) -> Channel:
  channel = Channel(
    _id = f'{type}_{item["title"]["simpleText"]}',
    type = type,
    title = item['title']['simpleText'],
    icon = item['icon']['thumbnails'][0]['url'],
    url = unquote(item['navigationEndpoint']['urlEndpoint']['url'].split('&q=')[-1])
  )
  return channel

def get_link(channel_uid: str) -> list:
  url = f'https://www.youtube.com/channel/{channel_uid}/about'
  request = requests.get(url)
  data = json.loads(re.findall(r'ytInitialData = (.+);\s*<\/script>', request.text)[0])

  link_list = []
  render = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][-2]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['channelAboutFullMetadataRenderer']
  link_list += [get_link_item(item, 'About') for item in render.get('primaryLinks', [])]

  render = data['header']['c4TabbedHeaderRenderer']
  headers = render.get('headerLinks', {}).get('channelHeaderLinksRenderer', {})
  link_list += [get_link_item(item, 'Header') for item in headers.get('primaryLinks', [])] + [get_link_item(item, 'Header') for item in headers.get('secondaryLinks', [])]

  return link_list

def get_recommend_item(item: dict, list: str) -> Channel:
  render = item.get('gridChannelRenderer') or item.get('channelRenderer')
  icon_url = render['thumbnail']['thumbnails'][-1]['url'].split('=s')[0]
  channel = Channel(
    _id = f'{list}_{render["channelId"]}',
    list = list,
    uid = render['channelId'],
    title = render['title']['simpleText'],
    icon = icon_url if icon_url.startswith('https:') else f'https:{icon_url}'
  )
  return channel

def get_recommend(channel_uid: str) -> list:
  url = f'https://www.youtube.com/channel/{channel_uid}/channels'
  request = requests.get(url, headers={'Accept-Language': 'ja-JP'})
  data = json.loads(re.findall(r'ytInitialData = (.+);\s*<\/script>', request.text)[0])

  recommend_list = []
  contents = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][-3]['tabRenderer']['content']['sectionListRenderer']['contents']
  for content in contents:
    content = content['itemSectionRenderer']['contents'][0]
    if 'gridRenderer' in content:
      items = content['gridRenderer']['items']
      recommend_list += [get_recommend_item(item, 'おすすめチャンネル') for item in items[:-1]]

      api_key = re.findall(r'"INNERTUBE_API_KEY":"([A-z0-9-]*)"', request.text)[0]
      continuation = re.findall(r'"continuationCommand":{"token":"([A-z0-9-%]*)"', request.text)[0]
      payload = {'context': {'client': {'clientName': 'WEB', 'clientVersion': '2.20230217.01.00'}}, 'continuation': continuation}
      url = f'https://www.youtube.com/youtubei/v1/browse?key={api_key}'
      data = requests.post(url, data = json.dumps(payload)).json()

      items = data['onResponseReceivedActions'][0]['appendContinuationItemsAction']['continuationItems']
      recommend_list += [get_recommend_item(item, 'おすすめチャンネル') for item in items]

    elif 'shelfRenderer' in content:
      title = content['shelfRenderer']['title']['runs'][0]['text']
      content = content['shelfRenderer']['content']

      items = content.get('horizontalListRenderer', {}).get('items', []) or content.get('expandedShelfContentsRenderer', {}).get('items', [])
      recommend_list += [get_recommend_item(item, title) for item in items]

  return recommend_list

if __name__ == '__main__':
  pass
