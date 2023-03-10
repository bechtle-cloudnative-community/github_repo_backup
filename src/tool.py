import os
import uuid
import requests

from config import myConfig


#-------------------------------------------------------------
class RepoGetter():
  api_base_url = "https://api.github.com"
  
  def __init__(self):
    os.makedirs(myConfig.backup_target_path, exist_ok=True)

    # self.api_repos_url = self.api_base_url + "/users/%s/repos" %myConfig.github_username
    
    # !!!repos of user detect by token!!!
    self.api_repos_url = self.api_base_url + "/user/repos" 
    
    self.headers = {
      "X-GitHub-Api-Version": myConfig.github_api_version,
      "Authorization": "Bearer %s" %myConfig.github_api_token
    }
    self.repos = []
  
  #----------------------------
  def get_repos_list(self):
    loop = True
    i = 0
    while loop:
      #---------
      i+=1
      try:
        req = requests.get(
          url= "%s?page=%s" %(self.api_repos_url, i),
          headers=self.headers 
        )
        req.raise_for_status()
      except requests.exceptions.HTTPError as err:
        loop = False
        raise SystemExit(err)
      #---------
      res = req.json()
      if not len(res):
        loop = False
        continue
      #---------
      for item in res:
        try: owner =  item["owner"]["login"]
        except: continue
        if owner.lower() == myConfig.github_username.lower():
          self.repos.append(item)
  
  #----------------------------
  def download_repo_archive(self, url:str, filename:str=None):
    #----------
    req = requests.get(
      url=url,
      headers=self.headers,
      allow_redirects=True
    )
    #----------
    if not filename:
      try:
        con_dis_str = req.headers["content-disposition"]
        filename = con_dis_str.split("=")[1]
      except Exception as e:
        print("Failed to get filename from url. Switching to uuid")
        filename = "%s.archive" %uuid.uuid4()

    #----------
    tgt_path = os.path.join(myConfig.backup_target_path, filename)
    with open(tgt_path, 'wb') as fl:
      fl.write(req.content)

  #----------------------------
  def batch_download_repos(self, print_info:bool=False):
    i = 0
    for item in self.repos:
      default_branch = item["default_branch"]
      repo_full_name = item["full_name"]
      dl_url = self.api_base_url + "/repos/%s/%s/%s" %(repo_full_name, myConfig.backup_format, default_branch)
      self.download_repo_archive(url=dl_url)

      if print_info:
        i+=1
        print("downloading repo ( %s of %s ): '%s'" %(i, len(self.repos), repo_full_name))
  
  #----------------------------
      
      
#-------------------------------------------------------------