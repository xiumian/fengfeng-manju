# 专业设计方法补强计划

日期：2026-11-17。authorization={explicit:true,user_request:"那你全面更新一下这些内容"}。
承接已确认方案：保留分层/权限/原文事实，补判断条件、选择取舍、执行细节、对照与纠错。不是另建生产系统。

## 范围与回退
- 7份：creation-preparation、action、camera、performance、vfx、sound、sampling。
- 4份：compile、performance-camera-methods、visual-impact-design、vfx-techniques。
- 仅配套新增本地来源登记、定向测试和验证记录。当前未发布8.2.1继续维护，不自动发布/安装/提交。不改模板、后台检查分离、48条库条目或工作台。
- 各文件本轮修改前副本与SHA在outputs/professional-method-update-20261117/before及before-manifest.json；保留之前未提交工作，不reset/clean。

## 实施顺序
1. 核查专业一手资料，来源登记区分全文可读、检索摘录、课程概览与未验证效果；提炼内容写入本地规则，链接只追溯，不默认联网。
2. 先建tests/test_professional_methods.py，对11份方法、实际context全文交接、来源登记和越界默认作定向回归；先见失败再改规则。
3. 每个文件按本职责补“如何从输入做选择”，附有代价的选项及修法；不强制所有场景输出分析表。保留已有具体方法，替换冲突默认而非末尾叠加。
4. 镜头先处理观看关系、空间/构图/运动与切点；动作处理目标/距离/支撑/应对及结果；表演与声音处理意图、变化与主次；扩写处理因果与许可；特效与采样处理机制/覆盖；编译处理融合。
5. 运行定向测试、原Python回归、活动包链接检查与保存CLI样例。用手写跨场景样例走真实交接并自审，明确不是独立模型实验或新视频实测。
6. 核对11份均覆盖；核对保护文件SHA未变。写maintenance/validation-professional-methods.md，记录实际命令和未验收项目。

## 验收边界
自动检查证明规则存在、实际提供、接口兼容与记录完整，不证明导演审美、自然语言理解、生成成功率或成片质量。自主综合的方法/案例明确标待实测，外部资料不作为所有拍法的统一强制标准。

## 执行记录
以上6步已执行。11份目标文件已补方法；13个来源ID本地登记；68项测试及包检查、历史CLI重放、3个原创文字案例与1板九格接口检查通过；10份保护文件哈希未变。详见validation-professional-methods.md及outputs/professional-method-update-20261117/after-manifest.json。完成的是规则维护和本地验证，不是成片验收。
