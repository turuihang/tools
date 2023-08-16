import asyncio
import hashlib
import json
import os.path
import os
import re
import time
import warnings
import aiofiles
import aiohttp

print("欢迎使用音乐下载器 v1.3.0")
print("请阅读以下使用须知：")
print("  1.本程序仅限个人使用，严禁商用！")
print("  2.本程序完全免费，若发现有商家售卖，请联系商家退款并举报！")
print("  3.本程序仅用作学习交流，若用户通过本下载器侵犯了第三方的权益，责任由用户自行承担！")
print("  4.使用本程序视为同意该须知！")
print("  5.本程序作者保留最终解释权！")
print("若不同意上述条款，请立即退出。")
time.sleep(3)
print("程序将在5秒后继续运行......")
time.sleep(5)
print("======更新日志v1.3.0======")
print("1.优化了警告提示。")
print("2.新功能：自动生成music文件夹")
print("3.优化了库文件，减轻运行压力")
print("")
time.sleep(1)

# pyinstaller -F -i icon.ico  --version-file file_version_info.txt MusicDownload.py
# 打包代码


print("输入你要爬取的歌曲或歌手（VIP音乐可能只能爬到1分钟）所下载的音乐将存放在程序目录下的music文件夹中")
target_name = input(">")
warnings.filterwarnings("ignore")  # 关闭警告，提升使用体验

path = os.getcwd() + "/"
save_path = path + "music/"
name = "music"
isExists = os.path.exists(save_path)
if not isExists:
    os.mkdir(save_path)
else:
    pass
# 在运行目录下生成名为“music”的文件夹
headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.114 Mobile Safari/537.36 "
}  # 设置用户UA


async def main(searchKeyWord, page='1'):
    async with aiohttp.ClientSession() as session:
        url = 'https://complexsearch.kugou.com/v2/search/song'
        t = time.time()
        params = {
            'callback': 'callback123',
            'page': page,
            'keyword': searchKeyWord,
            'pagesize': '40',
            'bitrate': '0',
            'isfuzzy': '0',
            'inputtype': '0',
            'platform': 'WebFilter',
            'userid': '0',
            'clientver': '2000',
            'iscorrection': '1',
            'privilege_filter': '0',
            'token': '',
            'srcappid': '2919',
            'clienttime': str(t),
            'mid': str(t),
            'uuid': str(t),
            'dfid': '-'
        }
        sign_params = ['NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt', 'bitrate=0', 'callback=callback123',
                       'clienttime=' + str(t), 'clientver=2000', 'dfid=-', 'inputtype=0', 'iscorrection=1',
                       'isfuzzy=0',
                       'keyword=' + searchKeyWord, 'mid=' + str(t), 'page=' + page, 'pagesize=30',
                       'platform=WebFilter', 'privilege_filter=0', 'srcappid=2919', 'token=', 'userid=0',
                       'uuid=' + str(t), 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt']
        sign_params = ''.join(sign_params)
        signature = hashlib.md5(sign_params.encode(encoding='UTF-8')).hexdigest()
        params['signature'] = signature
        async with session.get(url=url, headers=headers, params=params) as resp:
            if resp.status == 200:  # 如果返回值为200则获取歌曲列表
                resp_text = await resp.text()
                json_data = json.loads(resp_text[12:-2:])
                status = json_data['status']
                song_list = []
                if status == 1:
                    for item in json_data['data']['lists']:
                        song_info = {'SongName': re.sub(r"[\/\\\:\*\?\"\<\>\|]", "_", item['SongName']),
                                     'AlbumID': item['AlbumID'],
                                     'FileHash': item['FileHash'], 'SQFileHash': item['SQFileHash'],
                                     'HQFileHash': item['HQFileHash'], 'MvHash': item['MvHash'],
                                     'Audioid': item['Audioid'],
                                     'SingerName': re.sub(r"[\/\\\:\*\?\"\<\>\|]", "_", item['SingerName'])}
                        song_list.append(song_info)
                else:
                    print(f'[Warn]获取歌曲列表失败: {json_data["error_msg"]}')
                    time.sleep(10)
                tasks = []
                if len(song_list) > 0:
                    print(f'[INFO]获取歌曲列表成功，准备下载...')
                    time.sleep(0.1)
                    for song in song_list:
                        task = asyncio.create_task(getSongPlayAddr(song))
                        tasks.append(task)
                await asyncio.wait(tasks)
            else:
                print('[Warn]连接错误稍后重试： Fail_to_Connect')
                time.sleep(10)


async def getSongPlayAddr(song_info):
    async with aiohttp.ClientSession() as session:
        url = 'https://wwwapi.kugou.com/yy/index.php'
        params = {
            'r': 'play/getdata',
            'callback': 'jQuery191035601158181920933_1653052693184',
            'hash': song_info['FileHash'],
            'dfid': '2mSZvv2GejpK2VDsgh0K7U0O',
            'appid': '1014',
            'mid': 'c18aeb062e34929c6e90e3af8f7e2512',
            'platid': '4',
            'album_id': song_info['AlbumID'],
            '_': '1653050047389'
        }
        async with session.get(url=url, headers=headers, params=params) as resp:
            if resp.status == 200:
                resp_text = await resp.text()
                json_data = json.loads(resp_text[42:-2:].replace('\\', '').encode('utf8').decode('unicode_escape'))
                await saveMp3(json_data['data']['play_url'], song_info['SongName'], song_info['SingerName'])
            else:
                print('[Warn]请稍后再试： Time_Out')
                time.sleep(10)


async def saveMp3(url, song_name, singer_name):
    if not os.path.exists('music'):
        os.mkdir('music')
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            async with aiofiles.open(f'music/{song_name}-{singer_name}.mp3', mode='wb') as f:
                await f.write(await resp.content.read())
                print(f'{song_name}--{singer_name}--下载完成！')
                time.sleep(0.1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # 默认下载搜索列表的 第一页 共30首
    loop.run_until_complete(main(f'{target_name}'))
    time.sleep(100)

