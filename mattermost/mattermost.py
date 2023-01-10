"""Mattermost Sdk Apis.
#### 用户相关接口
    - get_channels 获取频道
    - get_wbs   获取webhooks
    - channel_bind_webhook 获取频道的webhook
    - get_a_webhook 随机获取一个webhook
    - get_user_by_email 通过邮箱获取账号信息
    - create_private_channel 创建私聊频道
"""

import ipaddress

from .utils import InnerRequest


class MattermostApi:
    def __init__(
        self,
        mattermost_user: str,
        mattermost_pwd: str,
        host: str,
        port: int,
        protocol="http",
        api_version="v4"
    ):
        """
        初始化
        Examples:
            >>> m_api = MattermostApi(
            >>>            mattermost_user = "xxxxxxxxxx",
            >>>            mattermost_pwd = "xxxxxxxxxx",
            >>>            host =  "127.0.0.1",
            >>>            port = 8883,
            >>>    )
        Args:
            mattermost_user: Mattermost账号
            mattermost_pwd:  Mattermost密码
            host:            Mattermost服务的IP地址
            port:            Mattermost服务的端口
            protocol:        filez的API版本（默认HTTP）
            api_version:     filez的API版本（默认v4）
        """
        assert protocol in ["http", "https"], "只支持http/https"
        try:
            ipaddress.IPv4Address(host)
        except ValueError:
            raise ValueError("参数'host': 请输入正确的 IPv4 地址.")
        self.server_url = f"{protocol}://{host}:{port}/api/{api_version}/"
        self.mattermost_user = mattermost_user
        self.mattermost_pwd = mattermost_pwd
        self.__refresh_token()

    @property
    def requests(self):
        return InnerRequest(headers=getattr(self, "auth_header", {}))

    def __refresh_token(self):
        url = self.server_url + "users/login"
        payload = {
            "login_id": self.mattermost_user,
            "password": self.mattermost_pwd
        }
        resp = self.requests.post(url, json=payload)
        headers = resp.headers
        data = resp.json()
        self.token = headers["Token"]
        self.login_user_id = data["id"]
        self.login_user_name = data["username"]
        self.auth_header = {"Authorization": f"Bearer {self.token}"}

    def __page_data(self, url, get_all=False):
        result = list()
        page = 0
        while True:
            resp = self.requests.get(url, params={"page": page})
            res_json = resp.json()
            if not res_json:
                break
            result.extend(res_json)
            if not get_all:
                break
            page += 1
        return result

    def get_channels(self, get_all: bool = False) -> list:
        """
        获取频道
        Examples:
            >>> get_channels(get_all=True)
        Args:
            get_all: 是否获取全部数据
        Returns:
            频道列表
            [{}, {}]
        """
        url = self.server_url + "channels"
        return self.__page_data(url, get_all=get_all)

    def get_wbs(self, get_all: bool = False) -> list:
        """
        获取Webhook(incoming)
        Examples:
            >>> get_wbs(get_all=True)
        Args:
            get_all: 是否获取全部数据
        Returns:
            Webhooks
            [{}, {}]
        """
        url = self.server_url + "hooks/incoming"
        return self.__page_data(url, get_all=get_all)

    def __create_wbs(self, channel_id, channel_name):
        """
        创建WEBHOOK
        """
        url = self.server_url + "hooks/incoming"
        payload = {
            "channel_id": channel_id,
            "user_id": self.login_user_id,
            "display_name": channel_name
        }
        resp = self.requests.post(url, json=payload)
        return resp.json()

    def channel_bind_webhook(self, channel_id: str, channel_name: str) -> str:
        """
        获取频道绑定的WEBHOOK或者给频道绑定WEBHOOK
        Examples:
            >>> channel_bind_webhook(get_all=True)
        Args:
            channel_id: 频道ID
            channel_name: 频道名称
        Returns:
            WebhookID
            "sadasasd79qwe7sdas"
        """
        web_hooks = self.get_wbs()
        bindwb_channels = [i["channel_id"] for i in web_hooks]

        # 频道未绑定WEBHOOK, 把WEBHOOK绑定到频道上
        if channel_id not in bindwb_channels:
            webhook_id = self.__create_wbs(channel_id, channel_name)
            return webhook_id["id"]

        # 频道已经绑定了WEBHOOK,直接返回WEBHOOK
        else:
            for i in web_hooks:
                if i["channel_id"] == channel_id:
                    return i["id"]

    def get_a_webhook(self) -> any([str, None]):
        """
        获取一个WebHookID
        Examples:
            >>> get_a_webhook()
        Args:
        Returns:
            WebhookID
            "sadasasd79qwe7sdas"
        """
        for webhook in self.get_wbs():
            if webhook["delete_at"] == 0:
                return webhook["id"]
        return None

    def get_user_by_email(self, email: str) -> dict:
        """
        通过邮箱获取Mattermost账号
        Examples:
            >>> get_user_by_email()
        Args:
            email: 邮箱
        Returns:
            用户信息字典
            {"usernmae": "xxxx", "email": "xxxx", "id": "sdsada"...}
        """
        url = self.server_url + f"users/email/{email}"
        resp = self.requests.get(url)
        return resp.json()

    def create_private_channel(self, email: str) -> dict:
        """
        创建私聊频道
        Examples:
            >>> create_private_channel()
        Args:
            email: 需要发起私聊账号的邮箱
        Returns:
            私聊频道信息
            {"name": "xxxx", "channel_name": "xxxx", "channel_id": "sdsada"...}
        """
        to_user_id = self.get_user_by_email(email)
        url = self.server_url + "channels/direct"
        payload = [self.login_user_id, to_user_id]
        resp = self.requests.post(url, json=payload)
        return resp.json()
