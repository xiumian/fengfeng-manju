# 工作台
只在启动、编辑、保存、导出时读取。入口assets/open-cowart-canvas/nine-grid.html，Windows启动九宫格.cmd，macOS 9宫.command。网页不自动生图，主稿保存video_master_prompt与历史。
events是完整事件，observation_draft只是九格派生预览；导入和单格修改均不得覆盖events或event_ids。正式完成需要events_complete=true及事件时间/映射检查。该字段由助手根据完整源文人工核对后写工作JSON；不是程序自动识别剧情完整的证明。
旧项目缺事件或确认时可编辑、保存，补齐源文映射与事件后再导入。主稿、事件、图各自保存；最终时长取完整事件end最大值，不把九格时长和当成片长。未确认时界面显示辅助草稿时长。
生成后实际看图，锁定版本和切片坐标进行局改。保存项目JSON跨设备使用；离线HTML包含程序、状态和图片。用户接受后才标完成，不从九格重建最终正文。
