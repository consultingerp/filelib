import json
import logging
import os, time
from datetime import datetime

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class ProcessConfig(models.Model):
    _name = 'process.config'
    _description = u'程序配置'

    name = fields.Char('程序名称', required=True)
    desc = fields.Char('程序描述')
    option_desc = fields.Char('操作描述')
    command_text = fields.Char('执行命令', required=True, help='os.system阻塞:Liunx系统命令请在命令后加 & (例 python hello.pyt &) '
                                                           'Windows请在命令前加 start   (例 start python hello.pyt) ')
    run_type = fields.Selection([('RUN', '继续运行'), ('RESTART', '重新运行'),
                                 ], '运行类型', required=True)
    enable = fields.Boolean('开启')
    check_time = fields.Datetime('检查时间')

    exe = fields.Char('bin路径')
    cwd = fields.Char('工作目录绝对路径')
    status = fields.Char('进程状态')
    create_time = fields.Datetime('进程创建时间')
    uids = fields.Char('uid信息')
    gids = fields.Char('gid信息')
    cpu_times = fields.Char('cpu时间信息')
    memory_percent = fields.Char('内存利用率')
    memory_info = fields.Char('内存')
    io_counters = fields.Char('IO信息')
    username = fields.Char('用户')

    @api.model
    def alive(self):
        _logger.debug("process.config Alive")
        process_list = self.search([('enable', '=', True)])
        for process in process_list:
            _logger.debug("process%s" % process)
            process_inof = self.process_runinfo(process, None)
            if not process_inof:  # 如果没有程序执行
                process.write({
                    "status": '',
                    'check_time': fields.Datetime.now()
                })

    @api.model
    def process_runinfo(self, process_info, pro_model=None):
        proesslist = psutil.pids()
        run_state = None
        for runproess in proesslist:
            proess = psutil.Process(runproess)
            if proess.is_running():
                try:
                    proess_name = proess.name();
                    if process_info.name in proess_name.lower():
                        _logger.info('结束进程%s' % proess_name)
                        option_desc = None
                        process_use_info = {
                            "exe": proess.exe(),
                            "cwd": proess.cwd(),
                            "status": proess.status(),
                            "create_time": datetime.fromtimestamp(proess.create_time()),
                            "uids": proess.pid,
                            "gids": proess.gids(),
                            "cpu_times": proess.cpu_times(),
                            "memory_percent": proess.memory_percent(),
                            "memory_info": proess.memory_info(),
                            "username": proess.username(),
                            'check_time': fields.Datetime.now()
                        }
                        if process_info.run_type == 'RESTART' and not pro_model:  # 如果是重新启动
                            proess.terminate()
                            proess.wait(timeout=10)
                            run_state = "END"
                            if process_info.command_text:
                                val = os.system(process_info.command_text)
                                _logger.info('重新运行程序%s:%s' % (proess_name, val))
                                run_state = "END_TO_START"
                                option_desc = '重新运行程序%s:%s' % (proess_name, val)
                        if pro_model == "KILL":
                            run_state = "KILL"
                            proess.terminate()
                            proess.wait(timeout=10)
                            option_desc = '结束程序%s' % proess_name
                        elif process_info.run_type == 'RUN':
                            run_state = "RUN"
                            option_desc = '程序正在运行%s，保持程序运行状态' % proess_name
                        process_use_info.update({"option_desc": option_desc})
                        process_info.write(process_use_info)
                except(psutil.ZombieProcess):
                    _logger.error('获取进程信息错误%s' % proess)
        if not run_state:
            val = os.system(process_info.command_text)
            _logger.info('运行程序%s:%s' % (process_info.name, val))
            if val == 0:
                process_info.write({"status": 'running',
                                    "create_time": datetime.fromtimestamp(proess.create_time()),
                                    "option_desc": '启动程序%s' % process_info.name
                                    })
            else:
                process_info.write({"status": 'error',
                                    "create_time": datetime.fromtimestamp(proess.create_time()),
                                    "option_desc": '执行命令错误%s' % val
                                    })

        return run_state

    @api.multi
    def end_process(self):
        self.ensure_one()
        self.process_runinfo(self, pro_model="KILL")
        self.write({
            "status": '',
            'check_time': fields.Datetime.now()
        })

    @api.multi
    def reset_process(self):
        self.ensure_one()
        self.process_runinfo(self)
