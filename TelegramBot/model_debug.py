from logic import detector

occupied, free, = detector.check_auto(mask="test_pizdec.mask", processed_image="test8.jpg", config_name="confwn")
freetext = f"\n{"=" * 10} Свободные места: {"=" * 10}\n"
occupiedtext = f"\n{"=" * 10} Занятые места: {"=" * 10}\n"
freemax = 0
occupiedmax = 0
for slot in free:
    freetext += f"🟢 {slot}\n"
    freemax += 1
for slot in occupied:
    occupiedtext += f"🔴 {slot}\n"
    occupiedmax += 1
endtext = f"\nВсего занято {occupiedmax} из {len(free) + len(occupied)}"
newtext = "ℹ️ **Информация по парковочным местам:**\n\n" + occupiedtext + freetext + endtext

print(newtext)