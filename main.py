# Python 3

import requests, json, pprint, datetime
import colorama

pp = pprint.PrettyPrinter(indent = 4)

def gen_dynamic_req(host_uid, offset_dynamic_id = 0):
	request_url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid=0"
	request_url += f"&host_uid={host_uid}&offset_dynamic_id={offset_dynamic_id}&need_top=1&platform=web"
	return requests.get(request_url)

if __name__ == "__main__":
	colorama.init()

	print("SimpleBiliDynamicView v0.1.0")
	print()
	user_uid = input("输入用户 UID 以开始: ")
	print()

	next_offset = 0
	continue_input = "y"
	cur_dynamic_count = 0
	while continue_input == "y":
		r = gen_dynamic_req(user_uid, next_offset).json()

		for i in r["data"]["cards"]:
			card_json = json.loads(i["card"])
			card_item = card_json["item"]
			cur_dynamic_count += 1
			text_transform_lambda = lambda x: x.replace("\n", "\n\t")

			if False:	# Raw json for debugging-purpose
				print(f"{colorama.Fore.CYAN}[DEBUG] 动态 #{cur_dynamic_count} JSON{colorama.Style.RESET_ALL}:")
				pp.pprint(card_json)
				continue

			dy_ts = None
			dy_ts_string = ""
			if "upload_time" in card_item:
				dy_ts = card_item["upload_time"]
			elif "timestamp" in card_item:
				dy_ts = card_item["timestamp"]
			elif "ctime" in card_json:
				dy_ts = card_json["ctime"]
			else:
				dy_ts_string = None
			if dy_ts_string == None:
				dy_ts_string = "*无法获取时间*"
			else:
				dy_ts_string = datetime.datetime.fromtimestamp(dy_ts).strftime('%Y-%m-%d %H:%M:%S')

			print(f"{colorama.Fore.CYAN}动态 #{cur_dynamic_count:05}{colorama.Style.RESET_ALL}: ({dy_ts_string})")
			if "short_link" in card_json:
				# (?) 1) Video dynamic
				print(f"\t视频: {card_json['short_link']}")
				print(f"\t视频封面: {card_json['pic']}")
			elif "content" in card_item:
				# (?) 1) Text-only dynamic (may contain metadata)
				print(f"\t「{text_transform_lambda(card_item['content'])}」")
				if "orig_dy_id" in card_item:
					# (?) 1) User dynamic with related content
					print("\t(关联来源: *已省略*)")
			elif "description" in card_item:
				# (?) 1) Dynamic with images
				print(f"\t「{text_transform_lambda(card_item['description'])}」")
				for (idx, img) in enumerate(card_item["pictures"], start=1):
					print(f"\t图片 {idx}: {img['img_src']}")
			else:
				# (?) Currently unknown dynamic type
				print("\t*未知类型的动态*")

		if r["data"]["has_more"] != 1:
			print("----- 动态到处结束 -----")
			break
		next_offset = r["data"]["next_offset"]
		continue_input = input("输入 `y` 以继续查看: ")

	print()
	print("感谢使用。")