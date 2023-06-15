import json, os, pymongo, re, requests, time
from datetime import datetime, timedelta
from discord import Embed

TIMEZONE = datetime.now() - datetime.utcnow()

async def wait_for_db():
  while True:
    try:
      client = pymongo.MongoClient('mongodb://db:27017/')
      client['youtube'].command('ping')
      break
    except pymongo.errors.ServerSelectionTimeoutError:
      time.sleep(1)

class MongoDB:
  def __init__(self, db: str, coll: str):
    client = pymongo.MongoClient('mongodb://db:27017/')
    self.collection = client[db][coll]

  def insert(self, *args: dict) -> None:
    self.collection.insert_many(args)

  def delete(self, query: dict) -> None:
    self.collection.delete_many(query)

  def update(self, query: dict, value: dict) -> None:
    self.collection.update_many(query, value)

  def find_one(self, query: dict = None) -> dict:
    return self.collection.find_one(query)

  def find(self, filter: dict = {}, sort: list = [], limit: int = 0) -> list:
    return list(self.collection.find(filter, sort=sort, limit=limit))

  def distinct(self, key: str, filter: dict = {}) -> list:
    return list(self.collection.distinct(key, filter=filter))
  
  def drop(self) -> None:
    self.collection.drop()

def get_item_list(old_list: list, new_list: list) -> list:
  all_ids = {item['_id'] for item in old_list} | {item._id for item in new_list}
  item_list = [(next((item for item in old_list if item['_id'] == id), None), next((item for item in new_list if item._id == id), None)) for id in all_ids]
  return item_list

def add_channel(channel_id: str, channel_title: str, discord_channel_id: int) -> None:
  try:
    MongoDB('youtube', 'channel').insert({'_id': channel_id, 'title': channel_title, 'discord': discord_channel_id})
    MongoDB('youtube', channel_id).insert(*[{'_id': video.id} for video in Youtube().get_playlistItem(channel_id)])
    return True
  except pymongo.errors.BulkWriteError:
    return False

def remove_channel(channel_id: str) -> None:
  coll = MongoDB('youtube', 'channel')
  data = coll.find({'_id': channel_id})
  if data:
    coll.delete({'_id': channel_id})
    MongoDB('youtube', channel_id).drop()
    return data['title']
  else:
    return False

def set_base_embed(name: str, url: str, icon: str) -> Embed:
  embed = Embed(color=0xff0000)
  embed.set_footer(text='Youtube', icon_url='https://imgur.com/8Ne5sku.png')
  embed.set_author(name=name, url=url, icon_url=icon)
  return embed

def set_embed(embed: Embed, **kwargs) -> Embed:
  embed = embed.copy()
  for attr, value in kwargs.items():
    if attr == 'image':embed.set_image(url=value)
    elif attr == 'thumbnail': embed.set_thumbnail(url=value)
    else: setattr(embed, attr, value)
  embed.timestamp = datetime.utcnow()
  return embed

def set_datetime(embed: Embed, video: object, type: str) -> Embed:
  match type:
    case 'scheduled':
      local_scheduled_time = video.scheduled_time + TIMEZONE
      embed.add_field(name=f'直播預定日期', value=local_scheduled_time.strftime('%Y年%m月%d日'), inline=True)
      embed.add_field(name=f'直播預定時間', value=local_scheduled_time.strftime('%H點%M分%S秒'), inline=True)
    case 'start':
      local_start_time = video.start_time + TIMEZONE
      embed.add_field(name=f'直播開始日期', value=local_start_time.strftime('%Y年%m月%d日'), inline=True)
      embed.add_field(name=f'直播開始時間', value=local_start_time.strftime('%H點%M分%S秒'), inline=True)
    case 'end':
      duration = datetime.strptime(str(video.end_time - video.start_time), '%H:%M:%S')
      local_end_time = video.end_time + TIMEZONE
      embed.add_field(name=f'直播結束日期', value=local_end_time.strftime('%Y年%m月%d日'), inline=True)
      embed.add_field(name=f'直播結束時間', value=local_end_time.strftime('%H點%M分%S秒'), inline=True)
      embed.add_field(name=f'直播總時長', value=duration.strftime('%H時%M分%S秒'), inline=True)
  return embed

def set_time_change(embed: Embed, original_time: datetime, changed_time: datetime) -> Embed:
  local_original_time = original_time + TIMEZONE
  local_changed_time = changed_time + TIMEZONE
  embed.add_field(name='【變更前】', value=local_original_time.strftime('%Y年%m月%d日\n%H點%M分%S秒'), inline=True)
  embed.add_field(name='【變更後】', value=local_changed_time.strftime('%Y年%m月%d日\n%H點%M分%S秒'), inline=True)
  return embed

def str_to_date(date_string: str = None) -> datetime:
  if not date_string: return None
  return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')

class Youtube:
  class Channel:
    def __init__(self, id: str, cid: str, title: str, icon: str) -> None:
      self.id = id
      self.cid = cid
      self.title = title
      self.icon = icon
      self.url = f'https://www.youtube.com/@{self.cid}'

  class Video:
    def __init__(self, id: str, **kwargs) -> None:
      self.id = id
      self.url = f'https://youtu.be/{self.id}'
      for attr, value in kwargs.items():
        setattr(self, attr, value)

  def get_youtube_data(self, path: str) -> dict:
    key = 'AIzaSyALBk1l0hF0mxidVlxSg4glO4shklgOdDE'
    url = f'https://www.googleapis.com/youtube/v3/{path}&key={key}'
    data = requests.get(url).json()
    return data

  def get_channel(self, channel_id: str) -> Channel:
    path = f'channels?part=snippet&id={channel_id}'
    data = self.get_youtube_data(path)

    if not data.get('items'): return None
    else:
      data = data['items'][0]
      channel = self.Channel(
        id = channel_id,
        cid = data['snippet']['customUrl'][1:],
        title = data['snippet']['title'],
        icon = self.get_thumbnail(data['snippet']['thumbnails'])
      )
      return channel

  def get_playlistItem(self, channel_id: str) -> list:
    playlist_id = 'UU' + channel_id[2:]
    path = f'playlistItems?part=snippet&playlistId={playlist_id}&maxResults=3'
    item_list = self.get_youtube_data(path)['items']
    video_list = [self.Video(id = item['snippet']['resourceId']['videoId']) for item in item_list]
    return video_list

  def get_video(self, video_id: str) -> Video:
    path = f'videos?part=contentDetails,liveStreamingDetails,snippet,statistics,status&id={video_id}'
    data = self.get_youtube_data(path)

    if not data.get('items'): return None
    else:
      data = data['items'][0]
      live_detail = data.get('liveStreamingDetails', {})
      video = self.Video(
        id = data['id'],
        title = data['snippet']['title'],
        thumbnail = self.get_thumbnail(data['snippet']['thumbnails']),
        status = data['snippet']['liveBroadcastContent'],
        published_time = str_to_date(data['snippet']['publishedAt']),
        scheduled_time = str_to_date(live_detail.get('scheduledStartTime')),
        start_time = str_to_date(live_detail.get('actualStartTime')),
        end_time = str_to_date(live_detail.get('actualEndTime'))
      )
      return video
    
  def get_videos(self, video_id_list: list) -> list:
    if not video_id_list: return []
    else:
      video_ids = ','.join(video_id_list[0:50])
      video_list = []
      path = f'videos?part=contentDetails,liveStreamingDetails,snippet,statistics,status&id={video_ids}'
      item_list = self.get_youtube_data(path)['items']
      for item in item_list:
        video = self.get_video_item(item)
        video_list.append(video)
      return video_list

  def get_thumbnail(self, data: dict) -> str:
    sizes = ['maxres', 'standard', 'high', 'medium', 'default']
    for size in sizes:
      if size in data:
        thumbnail = data[size]['url'].split('=s')[0].replace('_live', '')
        return thumbnail
    return 'https://imgur.com/2wAkxNb.png'

if __name__ == '__main__':
  data = Youtube().get_video('e0dfVZjaOq4')
  print(data)