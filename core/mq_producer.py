"""
RocketMQ全局异步生产者
"""
from rocketmq.client import Producer, Message
from config.settings import MQ_CONFIG


class MQProducer:
    """MQ生产者单例类"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MQProducer, cls).__new__(cls)
            cls._instance._producer = Producer(MQ_CONFIG['producer_group'])
            cls._instance._producer.set_name_server_address(MQ_CONFIG['namesrv_addr'])
            cls._instance._producer.start()
        return cls._instance
    
    def send_message(self, topic: str, tags: str, body: str):
        """发送消息"""
        msg = Message(topic)
        msg.set_tags(tags)
        msg.set_body(body)
        result = self._producer.send_sync(msg)
        return result
    
    def shutdown(self):
        """关闭生产者"""
        self._producer.shutdown()


# 创建全局MQ生产者实例
mq_producer = MQProducer()