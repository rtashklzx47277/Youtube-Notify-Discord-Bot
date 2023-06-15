import discord, json, os, tools
from discord.ext import tasks
from tools import MongoDB
from tools import Youtube

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

@client.command(name='help')
async def help(ctx) -> None:
  await ctx.send('help')

@client.command(name='add')
async def add(ctx, *channel_ids: str) -> None:
  discord_channel_id = ctx.channel.id
  for channel_id in channel_ids:
    channel = Youtube().get_channel(channel_id)
    if not channel: await ctx.send('查無此頻道，請檢查頻道ID是否有誤！')
    else:
      response = tools.add_channel(channel_id, channel.title, discord_channel_id)
      if response:
        await ctx.send(f'已新增***{channel.title}***至關注列表！')
      else:
        await ctx.send(f'關注列表中已有***{channel.title}***！')

@client.command(name='remove')
async def remove(ctx, *channel_ids: str) -> None:
  for channel_id in channel_ids:
    response = tools.remove_channel(channel_id)
    if response:
      await ctx.send(f'已自關注列表中移除***{response["title"]}***！')
    else:
      await ctx.send('關注列表中找不到此頻道！')

@client.event
async def on_ready():
  await tools.wait_for_db()
  await livestream_notify.start()

@tasks.loop(seconds=60)
async def livestream_notify():
  try:
    channel_data = MongoDB('youtube', 'channel').find()

    for channel_info in channel_data:
      channel_id, discord_channel_id = channel_info['_id'], channel_info['discord']
      discord_channel = client.get_channel(discord_channel_id)

      channel = Youtube().get_channel(channel_id)
      base_embed = tools.set_base_embed(channel.title, channel.url, channel.icon)

      coll = MongoDB('youtube', channel_id)
      video_id_list = coll.distinct('_id')
      for video in Youtube().get_playlistItem(channel_id): 
        if video.id not in video_id_list:
          video = Youtube().get_video(video.id)
          if not video.scheduled_time:
            embed = tools.set_embed(base_embed, title=video.title, description='上傳了新影片！', url=video.url, image=video.thumbnail)
            await discord_channel.send(embed=embed)
          elif video.status == 'upcoming':
            embed = tools.set_embed(base_embed, title=video.title, description='建立了新的待機台！', url=video.url, image=video.thumbnail)
            embed = tools.set_datetime(embed, video, 'scheduled')
            await discord_channel.send(embed=embed)
          coll.insert({'_id': video.id, 'title': video.title, 'time': video.published_time, 'scheduled_time': video.scheduled_time})

      for video_item in tools.get_item_list(coll.find(), Youtube().get_videos(coll.distinct('_id'))):
        video_data, video = video_item
        if not video:
          embed = tools.set_embed(base_embed, title=video_data['title'], description='預定直播已被取消了！', url=f'https://youtu.be/{video_data["_id"]}')
          await discord_channel.send(embed=embed)
          coll.delete({'_id': video_data['_id']})

        else:
          if video.scheduled_time != video_data['time']:
            embed = tools.set_embed(base_embed, title=video.title, description='直播預定時間變更了！', url=video.url, image=video.thumbnail)
            embed = tools.set_time_change(embed, video_data['time'], video.scheduled_time)
            await discord_channel.send(embed=embed)
            coll.update({'_id': video._id}, {'$set': {'time': video.scheduled_time}})

          if video.status == 'live' and video_data['status'] == 'upcoming':
            embed = tools.set_embed(base_embed, title=video.title, description='直播串流開始了！', url=video.url, image=video.thumbnail)
            embed = tools.set_datetime(embed, video, 'start')
            await discord_channel.send(embed=embed)
            coll.update({'_id': video._id}, {'$set': {'status': video.status}})

          if video.status == 'none' and video_data['status'] == 'live':
            embed = tools.set_embed(base_embed, title=video.title, description='直播串流結束了！', url=video.url, image=video.thumbnail)
            embed = tools.set_datetime(embed, video, 'end')
            await discord_channel.send(embed=embed)
            coll.delete({'_id': video._id})
  except: pass

client.run(os.getenv('DISCORD_TOKEN'))
