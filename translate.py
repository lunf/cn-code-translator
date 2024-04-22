from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import os
import re
import time
from time import strftime
from time import gmtime


model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

def translate_from_to(from_lang="zh", to_lang="en", text=""):
    tokenizer.src_lang = from_lang
    encoded_text = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(**encoded_text, max_new_tokens=4000, forced_bos_token_id=tokenizer.get_lang_id(to_lang))
    text_translated = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return text_translated[0]

def group_chinese_words(str):
    regex = r"[\u4e00-\ufaff]+|[0-9-_ ]+|[a-zA-Z]+\'*[a-z]*"
    matches = re.findall(regex, str, re.UNICODE)

    results = []
    chinese_text = ''
    for char in matches :
        # Find Chinese char then append otherwise reset for new word
        if not char.isascii():
            results.append(char)
            chinese_text = ''
        else:
            results.append(chinese_text)
            chinese_text = ''

    # If last item is Chinese then added to the array
    if chinese_text != '':
        results.append(chinese_text)
    
    # Remove the empty
    return list(filter(None, results))

def translate_file(fpath):
    start = time.time()
    out = open(fpath+'.tmp', 'w')
    with open(fpath, 'r') as f:
        lines = f.readlines()

        for line in lines:
            if not line.isascii():
                
                for character in group_chinese_words(line):
                    translated = translate_from_to('zh', 'en', character)
                    # only first match
                    line = line.replace(character, translated, 1)
                out.write(line)
            else:
                out.write(line)
        
    out.close()
    os.rename(fpath+'.tmp', fpath)
    print('File: {}, It took {} '.format(os.path.basename(fpath), strftime("%H:%M:%S", gmtime(time.time() - start))))

def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".ico") or filename.endswith(".jpg") or filename.endswith(".gif") or filename.endswith(".svg") or filename.endswith(".png") or filename.endswith(".gitignore") or filename.endswith(".docx"):
                continue
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            # Ignored .git folder
            if filepath.find(".git") < 0:
                file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

def translate_project():
    start = time.time()
    # specify folder
    folder = '/home/username/Documents/github/source'
    # get files
    full_file_paths = get_filepaths(folder)

    for file in full_file_paths:
        print('Processing...'+file)
        translate_file(file)

    print('Completed. It took {} '.format(strftime("%H:%M:%S", gmtime(time.time() - start))))


#print(group_chinese_words("-- 7、角色和菜单关联表  角色1-N菜单"))
#print(group_chinese_words("length.not.valid=长度必须在{min}到{max}个字符之间"))
#print(group_chinese_words("no.permission=您没有数据的权限，请联系管理员添加权限 [{0}]"))
translate_project()
#get_filepaths('/home/username/Documents/github/source')
#translate_file('/home/username/Documents/github/source/messages.properties')
