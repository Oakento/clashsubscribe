import os
import asyncio
import urllib.request
import yaml

async def fetch(source):
    print('Downloading config from {}...'.format(source['name']))
    req = urllib.request.Request(
        url=source['url'],
        headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,zh-TW;q=0.8,zh;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8')
        print("Successfully downloaded {} configuration.".format(source['name']))
        return html
    except:
        print("Downloading {} configuration file failed.".format(source['name']))

async def main():
    path = os.path.abspath(os.path.dirname(__file__))
    with open(path + '/config.yaml') as f:
        local_config = yaml.safe_load(f)
        clash_template_path = local_config['clash-template-path']
        clash_config_path = local_config['clash-config-path']
        source_list = local_config['source']
    download_list = await asyncio.gather(
        *[fetch(source) for source in source_list]
    )
    with open(clash_template_path, 'r') as orif:
        new_conf = yaml.safe_load(orif)
    for download in download_list:
        if download is None:
            continue
        conf_dict = yaml.safe_load(download)
        if not isinstance(conf_dict, dict) or conf_dict.get('proxies') is None:
            continue
        new_conf['proxies'] += conf_dict['proxies']
        new_conf['proxy-groups'][0]['proxies'] += [proxy['name'] for proxy in conf_dict['proxies']]
    with open(clash_config_path, 'w') as newf:
        yaml.safe_dump(new_conf, newf, allow_unicode=True)
        print('done.')

if __name__ == '__main__':
    asyncio.run(main())

