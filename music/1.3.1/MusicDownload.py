import asyncio
import hashlib
import json
import os
import re
from time import time, sleep
from warnings import filterwarnings

import aiofiles
import aiohttp


# 清屏函数
def screen_clear():
    if os.name == 'posix':  # 在MacOS或Linux系统运行时
        os.system('clear')
        pass
    else:  # 在Windows系统运行时 os.name == 'nt'
        os.system('cls')
        pass


print('')
print('')
print('     ___        ___       _______')
print('    / _ \\      / _ \\      | ---- \\')
print('   / / \\ \\    / / \\ \\     | |  |  \\')
print('  / /   \\ \\  / /   \\ \\    | |  |  |')
print(' / /     \\ \\/ /     \\ \\   | |__/ /')
print('/_/       \\__/       \\_\\  |_____/  ')
print('')
print('')
print("欢迎使用音乐下载器 v1.3.1")
print("请阅读以下使用须知：")
print("  1.本程序仅限个人使用，严禁商用！")
print("  2.本程序完全免费，若发现有商家售卖，请联系商家退款并举报！")
print("  3.本程序仅用作学习交流，若用户通过本下载器侵犯了第三方的权益，责任由用户自行承担！")
print("  4.使用本程序视为同意该须知！")
print("  5.本程序作者保留最终解释权！")
print("若不同意上述条款，请立即退出。")
sleep(3)
print("程序将在5秒后继续运行......")
sleep(5)
os.system('cls' if os.name == 'nt' else 'clear')
print('')
print('')
print("======更新日志v1.3.1======")
print("1.提示信息易读化")
print("2.优化了针对歌曲判断的正则表达式")
print("3.添加了开屏Logo")
print('')
print('')

# pyinstaller -F -i icon.ico  --version-file file_version_info.txt MusicDownload.py
# 打包代码


print("输入你要爬取的歌曲或歌手（VIP音乐可能只能爬到1分钟）所下载的音乐将存放在程序目录下的music文件夹中")
kw = input(">")

filterwarnings("ignore")  # 关闭系统警告，提升使用体验

# run_path 程序运行路径
# save_path 保存路径
run_path = os.getcwd() + "/"
save_path = run_path + "music/"
folder_name = "music"
isExists = os.path.exists(save_path)
if not isExists:
    os.mkdir(save_path)  # 如果当前目录下没有music文件夹则生成
else:
    pass  # 如果已存在music文件夹则跳过
# 在运行目录下生成名为“music”的文件夹


headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.114 Mobile Safari/537.36 "
}  # 设置用户UA


async def main(searchKeyWord, page='1'):
    async with aiohttp.ClientSession() as session:
        url = 'https://complexsearch.kugou.com/v2/search/song'
        t = time()
        params = {
            'callback': 'callback123',
            'page': page,
            'keyword': searchKeyWord,
            'pagesize': '30',
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
            if resp.status == 200:  # 如果http响应为200则获取歌曲列表
                resp_text = await resp.text()
                json_data = json.loads(resp_text[12:-2:])
                status = json_data['status']
                song_list = []
                if status == 1:
                    for item in json_data['data']['lists']:
                        song_info = {'SongName': re.sub(r"[[/]\\:*?\"<>|]", "_", item['SongName']),
                                     'AlbumID': item['AlbumID'],
                                     'FileHash': item['FileHash'], 'SQFileHash': item['SQFileHash'],
                                     'HQFileHash': item['HQFileHash'], 'MvHash': item['MvHash'],
                                     'Audioid': item['Audioid'],
                                     'SingerName': re.sub(r"[[/]\\:*?\"<>|]", "_", item['SingerName'])}
                        song_list.append(song_info)
                else:
                    print(f'[Warn]获取歌曲列表失败: {json_data["error_msg"]}')
                    sleep(10)
                tasks = []
                if len(song_list) > 0:
                    print(f'[INFO]获取歌曲列表成功，准备下载...')
                    sleep(0.1)
                    for song in song_list:
                        task = asyncio.create_task(getSongPlayAddr(song))
                        tasks.append(task)
                await asyncio.wait(tasks)
            else:  # http未正确响应
                print('[Warn]连接错误稍后重试： Fail_to_Connect')
                sleep(10)


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
                # detection_objects = json.loads(json_data)
                # if 'play_url' in detection_objects['song']:
                #     await saveMp3(json_data['data']['play_url'], song_info['SongName'], song_info['SingerName'])
                # else:
                #     pass
                await saveMp3(json_data['data']['play_url'], song_info['SongName'], song_info['SingerName'])
            else:
                print('[Warn]请稍后再试： Time_Out')
                sleep(10)


async def saveMp3(url, song_name, singer_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            async with aiofiles.open(f'music/{song_name}-{singer_name}.mp3', mode='wb') as f:
                await f.write(await resp.content.read())
                print(f'{song_name} by {singer_name}--下载完成！')
                sleep(0.15)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # 默认下载搜索列表的 第一页 共30首
    loop.run_until_complete(main(f'{kw}'))
    sleep(10)
