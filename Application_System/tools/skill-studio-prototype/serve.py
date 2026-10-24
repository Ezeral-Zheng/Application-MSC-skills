#!/usr/bin/env python3
"""PROTOTYPE: a read-only skill catalogue and local workflow designer."""
import argparse
import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT.parents[1] / 'skills'
SPECS = {
 'student-material-normalizer': ('资料标准化','准备','原始附件、学生目录','Markdown 资料与完整性检查','把分散资料变成后续节点能够读取的事实源。'),
 'personalization-material-importer': ('个性化素材','准备','问卷、动机、已有经历','已确认素材与待确认问题','区分真实经历、推断与未来规划。'),
 'tencent-program-importer': ('目标专业导入','准备','专业库、腾讯择校表','匹配计划与目标信息','含腾讯表格写入动作，执行前有其自身确认要求。'),
 'ps-narrative-matrix': ('学生版叙事矩阵','规划','事实资料、目标专业、原有矩阵','六列总览与九字段叙事卡','同校不同专业优先拉开主线，跨校同方向允许适度复用。'),
 'personal-statement-writer': ('个人陈述写作','写作','资料、目标、矩阵、学生偏好','双语 PS 内部候选稿','按核心问题选择经历；正式交付还需完整审查。'),
 'recommendation-letter-writer': ('推荐信写作','写作','推荐人交集、课程与学生事实','推荐人口吻的推荐信','两封推荐信采用不同证据与结构。'),
 'resume-experience-writer': ('项目经历整理','写作','课程项目 Markdown','英文经历片段与未纳入说明','只整理事实完整的项目，作为简历素材。'),
 'resume-application-pipeline': ('简历完整流程','组合流程','学生材料、用途与格式要求','审核后的简历及可选 Word','包含素材整理、定向写作、事实审查、质量审查与修改。'),
 'resume-writer': ('英文简历写作','写作','已核实经历、用途与布局','英文简历候选稿','实际简历任务应由简历完整流程统一编排。'),
 'targeted-one-page-resume-writer': ('定向一页简历','写作','目标项目、可用经历','目标专属一页简历','根据目标筛选经历与课程，属于简历流程内部阶段。'),
 'academic-resume-format': ('升学简历格式','组合流程','实习、科研、课程与活动','经历库与统一简历结构','先整理可追溯经历，再组织简历。'),
 'application-review': ('事实与格式审查','审查','当前候选稿、来源与类型要求','Pass / Needs Fix / Blocked','事实、来源、格式与版本门禁，不等于独立内容审稿。'),
 'external-application-review': ('独立内容审稿','审查','当前稿与最小审稿输入包','Pass / Revise / Blocked','每轮需要全新且不继承历史的审稿人；只写报告。'),
 'resume-quality-review': ('简历质量审查','审查','已通过事实审查的简历','六维质量报告','在事实审查之后判断目标适配、表达与版面质量。'),
 'application-revision': ('文书修改','修改','当前稿、净化问题单、最小事实包','下一内部候选稿','隔离修改不能继承完整评分或历史稿，修改后重新审查。'),
 'ps-word-export': ('PS Word 导出','交付','已通过全部门禁的正式 PS','桌面学生目录下的 Word','只导出正式 PS 的英文部分，不负责写作。'),
 'resume-word-generator': ('简历 Word 导出','交付','审核后的 Markdown、布局要求','Word 与版面验收','由简历流程调用，导出后还要检查渲染。'),
 'student-style-memory': ('学生偏好沉淀','交付','正式交付后的反馈','学生偏好局部更新','只沉淀风格偏好，系统错误进入审查记忆。'),
}

def catalogue():
 result=[]
 for p in sorted(SKILLS.glob('*/SKILL.md')):
  raw=p.read_text(encoding='utf-8')
  key=p.parent.name
  spec=SPECS.get(key,(key,'其他','查看原始 skill','查看原始 skill','读取原始规则理解输入输出。'))
  description=re.search(r'^description:\s*(.+)$',raw,re.M)
  result.append(dict(id=key,title=spec[0],category=spec[1],input=spec[2],output=spec[3],summary=spec[4],description=description.group(1) if description else '',path=str(p),source=raw))
 return result

class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,directory=str(ROOT),**kwargs)
 def do_GET(self):
  if self.path.split('?')[0]=='/catalog.json':
   body=json.dumps(catalogue(),ensure_ascii=False).encode()
   self.send_response(200)
   self.send_header('Content-Type','application/json; charset=utf-8')
   self.send_header('Cache-Control','no-store')
   self.send_header('Content-Length',str(len(body)))
   self.end_headers();self.wfile.write(body)
  else:
   super().do_GET()
 def log_message(self,*args):
  pass

if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--port',type=int,default=8765)
 args=parser.parse_args()
 print(f'Prototype: http://127.0.0.1:{args.port}/?variant=A',flush=True)
 ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
