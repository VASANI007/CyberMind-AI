import re

def main():
    path = "services/email_support_service.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. User confirmation card 1 user icon
    old1 = '''<div style="width:36px; height:36px; border-radius:50%; background:#162036; border:1px solid rgba(0, 210, 255, 0.35); text-align:center; line-height:36px; font-size:16px;">
                            👤
                          </div>'''
    new1 = '''<div style="width:36px; height:36px; border-radius:50%; background:#162036; border:1px solid rgba(0, 210, 255, 0.35); text-align:center; line-height:36px;">
                            <img src="https://cdn-icons-png.flaticon.com/512/9131/9131529.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />
                          </div>'''
    
    # 2. Timeline notice clock
    old2 = '''<div style="width:26px; height:26px; border-radius:50%; background:rgba(0, 210, 255, 0.15); border:1px solid rgba(0, 210, 255, 0.4); text-align:center; line-height:26px; font-size:13px;">
                            🕒
                          </div>'''
    new2 = '''<div style="width:26px; height:26px; border-radius:50%; background:rgba(0, 210, 255, 0.15); border:1px solid rgba(0, 210, 255, 0.4); text-align:center; line-height:26px;">
                            <img src="https://cdn-icons-png.flaticon.com/512/10473/10473481.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" />
                          </div>'''

    # 3. Ticket details header
    old3 = '''<span style="color:#38BDF8; margin-right:6px;">📑</span> YOUR TICKET DETAILS'''
    new3 = '''<img src="https://cdn-icons-png.flaticon.com/512/16782/16782995.png" width="15" height="15" style="vertical-align:middle; display:inline-block; margin-right:6px;" alt="" /> YOUR TICKET DETAILS'''

    # 4. Table icons: Subject, Email, Time, Message
    old4 = '''<span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(59, 130, 246, 0.15); border:1px solid rgba(59, 130, 246, 0.4); color:#3B82F6; text-align:center; line-height:22px; font-size:11px;">📄</span>'''
    new4 = '''<span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(59, 130, 246, 0.15); border:1px solid rgba(59, 130, 246, 0.4); text-align:center; line-height:22px;"><img src="https://cdn-icons-png.flaticon.com/512/2210/2210197.png" width="12" height="12" style="vertical-align:middle; display:inline-block;" alt="" /></span>'''

    old5 = '''<span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(6, 182, 212, 0.15); border:1px solid rgba(6, 182, 212, 0.4); color:#06B6D4; text-align:center; line-height:22px; font-size:11px;">✉️</span>'''
    new5 = '''<span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(6, 182, 212, 0.15); border:1px solid rgba(6, 182, 212, 0.4); text-align:center; line-height:22px;"><img src="https://cdn-icons-png.flaticon.com/512/888/888853.png" width="12" height="12" style="vertical-align:middle; display:inline-block;" alt="" /></span>'''

    old6 = '''<span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(236, 72, 153, 0.15); border:1px solid rgba(236, 72, 153, 0.4); color:#EC4899; text-align:center; line-height:22px; font-size:11px;">📅</span>'''
    new6 = '''<span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(236, 72, 153, 0.15); border:1px solid rgba(236, 72, 153, 0.4); text-align:center; line-height:22px;"><img src="https://cdn-icons-png.flaticon.com/512/10692/10692035.png" width="12" height="12" style="vertical-align:middle; display:inline-block;" alt="" /></span>'''

    old7 = '''<span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(139, 92, 246, 0.15); border:1px solid rgba(139, 92, 246, 0.4); color:#8B5CF6; text-align:center; line-height:22px; font-size:11px;">💬</span>'''
    new7 = '''<span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(139, 92, 246, 0.15); border:1px solid rgba(139, 92, 246, 0.4); text-align:center; line-height:22px;"><img src="https://cdn-icons-png.flaticon.com/512/3790/3790214.png" width="12" height="12" style="vertical-align:middle; display:inline-block;" alt="" /></span>'''

    # 5. User confirmation 4 pillars
    old8 = '''<div style="width:28px; height:28px; border-radius:50%; background:rgba(0, 210, 255, 0.12); border:1px solid rgba(0, 210, 255, 0.35); text-align:center; line-height:28px; font-size:13px; margin:0 auto 6px auto;">🛡️</div>'''
    new8 = '''<div style="width:28px; height:28px; border-radius:50%; background:rgba(0, 210, 255, 0.12); border:1px solid rgba(0, 210, 255, 0.35); text-align:center; line-height:28px; margin:0 auto 6px auto;"><img src="https://cdn-icons-png.flaticon.com/512/6071/6071531.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></div>'''

    old9 = '''<div style="width:28px; height:28px; border-radius:50%; background:rgba(168, 85, 247, 0.12); border:1px solid rgba(168, 85, 247, 0.35); text-align:center; line-height:28px; font-size:13px; margin:0 auto 6px auto;">📊</div>'''
    new9 = '''<div style="width:28px; height:28px; border-radius:50%; background:rgba(168, 85, 247, 0.12); border:1px solid rgba(168, 85, 247, 0.35); text-align:center; line-height:28px; margin:0 auto 6px auto;"><img src="https://cdn-icons-png.flaticon.com/512/404/404621.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></div>'''

    old10 = '''<div style="width:28px; height:28px; border-radius:50%; background:rgba(59, 130, 246, 0.12); border:1px solid rgba(59, 130, 246, 0.35); text-align:center; line-height:28px; font-size:13px; margin:0 auto 6px auto;">⚙️</div>'''
    new10 = '''<div style="width:28px; height:28px; border-radius:50%; background:rgba(59, 130, 246, 0.12); border:1px solid rgba(59, 130, 246, 0.35); text-align:center; line-height:28px; margin:0 auto 6px auto;"><img src="https://cdn-icons-png.flaticon.com/512/4870/4870942.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></div>'''

    old11 = '''<div style="width:28px; height:28px; border-radius:50%; background:rgba(34, 197, 94, 0.12); border:1px solid rgba(34, 197, 94, 0.35); text-align:center; line-height:28px; font-size:13px; margin:0 auto 6px auto;">👥</div>'''
    new11 = '''<div style="width:28px; height:28px; border-radius:50%; background:rgba(34, 197, 94, 0.12); border:1px solid rgba(34, 197, 94, 0.35); text-align:center; line-height:28px; margin:0 auto 6px auto;"><img src="https://cdn-icons-png.flaticon.com/512/921/921347.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></div>'''

    # 6. Admin email badge: Bell
    old12 = '''<td style="vertical-align:middle; padding-right:8px; font-size:14px; line-height:1;">🔔</td>'''
    new12 = '''<td style="vertical-align:middle; padding-right:8px; line-height:1;"><img src="https://cdn-icons-png.flaticon.com/512/18421/18421884.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></td>'''

    # 7. Admin Card 1: User Info header
    old13 = '''<div style="display:inline-block; width:24px; height:24px; border-radius:6px; background:#1D4ED8; text-align:center; line-height:24px; font-size:12px; vertical-align:middle; margin-right:8px;">👤</div>'''
    new13 = '''<div style="display:inline-block; width:24px; height:24px; border-radius:6px; background:#1D4ED8; text-align:center; line-height:24px; vertical-align:middle; margin-right:8px;"><img src="https://cdn-icons-png.flaticon.com/512/9131/9131529.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></div>'''

    # 8. Admin Card 1: Rows
    old14 = '''<span style="display:inline-block; width:20px; color:#38BDF8;">👤</span> User Name:'''
    new14 = '''<span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/9131/9131529.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> User Name:'''

    old15 = '''<span style="display:inline-block; width:20px; color:#38BDF8;">✉️</span> User Email:'''
    new15 = '''<span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/888/888853.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> User Email:'''

    old16 = '''<span style="display:inline-block; width:20px; color:#38BDF8;">📄</span> Subject:'''
    new16 = '''<span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/2210/2210197.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> Subject:'''

    old17 = '''<span style="display:inline-block; width:20px; color:#38BDF8;">#️⃣</span> Ticket ID:'''
    new17 = '''<span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/16782/16782995.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> Ticket ID:'''

    old18 = '''<span style="display:inline-block; width:20px; color:#38BDF8;">📅</span> Submitted Time:'''
    new18 = '''<span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/10692/10692035.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> Submitted Time:'''

    # 9. Admin Card 2: Problem Description header & icon
    old19 = '''<div style="display:inline-block; width:24px; height:24px; border-radius:6px; background:#2563EB; text-align:center; line-height:24px; font-size:12px; vertical-align:middle; margin-right:8px;">💬</div>'''
    new19 = '''<div style="display:inline-block; width:24px; height:24px; border-radius:6px; background:#2563EB; text-align:center; line-height:24px; vertical-align:middle; margin-right:8px;"><img src="https://cdn-icons-png.flaticon.com/512/3790/3790214.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></div>'''

    old20 = '''<div style="width:30px; height:30px; border-radius:50%; background:#132147; border:1px solid #2563EB; text-align:center; line-height:30px; font-size:13px;">
                              💬
                            </div>'''
    new20 = '''<div style="width:30px; height:30px; border-radius:50%; background:#132147; border:1px solid #2563EB; text-align:center; line-height:30px;">
                              <img src="https://cdn-icons-png.flaticon.com/512/3790/3790214.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" />
                            </div>'''

    # 10. Admin Card 3: Response Guideline timer
    old21 = '''<div style="width:34px; height:34px; border-radius:50%; background:rgba(0, 210, 255, 0.12); border:1px solid #00D2FF; text-align:center; line-height:34px; font-size:16px;">
                        ⏱️
                      </div>'''
    new21 = '''<div style="width:34px; height:34px; border-radius:50%; background:rgba(0, 210, 255, 0.12); border:1px solid #00D2FF; text-align:center; line-height:34px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/2055/2055768.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />
                      </div>'''

    # 11. Admin Reply button
    old22 = '''✉️ &nbsp; Reply Directly to {name}'''
    new22 = '''<img src="https://cdn-icons-png.flaticon.com/512/888/888853.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /> &nbsp; Reply Directly to {name}'''

    # 12. Admin 4 Pillars
    old23 = '''<span style="font-size:16px;">🛡️</span>'''
    new23 = '''<img src="https://cdn-icons-png.flaticon.com/512/6071/6071531.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />'''

    old24 = '''<span style="font-size:16px;">📊</span>'''
    new24 = '''<img src="https://cdn-icons-png.flaticon.com/512/404/404621.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />'''

    old25 = '''<span style="font-size:16px;">⚙️</span>'''
    new25 = '''<img src="https://cdn-icons-png.flaticon.com/512/4870/4870942.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />'''

    old26 = '''<span style="font-size:16px;">👥</span>'''
    new26 = '''<img src="https://cdn-icons-png.flaticon.com/512/921/921347.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />'''

    all_pairs = [
        (old1, new1), (old2, new2), (old3, new3), (old4, new4),
        (old5, new5), (old6, new6), (old7, new7), (old8, new8),
        (old9, new9), (old10, new10), (old11, new11), (old12, new12),
        (old13, new13), (old14, new14), (old15, new15), (old16, new16),
        (old17, new17), (old18, new18), (old19, new19), (old20, new20),
        (old21, new21), (old22, new22), (old23, new23), (old24, new24),
        (old25, new25), (old26, new26)
    ]

    count = 0
    for old, new in all_pairs:
        if old in content:
            content = content.replace(old, new)
            count += 1
        else:
            # Try stripping carriage returns
            old_c = old.replace("\r\n", "\n")
            if old_c in content:
                content = content.replace(old_c, new)
                count += 1
            else:
                print("FAILED TO MATCH:", repr(old[:40]))

    print(f"Successfully replaced {count} of {len(all_pairs)} items in email_support_service.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
