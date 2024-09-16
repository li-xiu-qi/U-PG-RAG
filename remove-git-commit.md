### 1. **备份现有仓库**

在操作前，最好先备份你的现有仓库，以防意外丢失重要数据。

```bash
cp -r <your-repo> <your-repo-backup>
```

### 2. **删除历史记录并保留当前状态**

1. **创建一个新的分支**：

   切换到一个新的分支，暂时保存当前的状态：

   ```bash
   git checkout --orphan temp-branch
   ```

2. **删除所有文件和目录**：

   删除所有文件，并提交当前状态：

   ```bash
   git rm -rf .
   git commit --allow-empty -m "Initial commit with current state"
   ```

3. **删除旧的分支**：

   删除旧的分支并重命名当前的分支：

   ```bash
   git branch -D main   # 删除旧的主分支
   git branch -m main   # 将当前分支重命名为 main
   ```

4. **强制推送到远程仓库**：

   强制推送到远程仓库，覆盖所有历史记录：

   ```bash
   git push --force origin main
   ```

### 3. **清理本地仓库**

删除 Git 的引用和垃圾回收，以确保没有旧的历史记录残留：

```bash
rm -rf .git/refs/original/
git reflog expire --expire=now --all-ref
git gc --prune=now --aggressive
```

### 总结

- **备份**：先备份你的仓库。
- **创建新分支**：切换到新的分支，删除所有文件并提交。
- **删除旧分支**：删除旧的分支并将新的分支重命名为主分支。
- **强制推送**：将新状态推送到远程仓库，覆盖所有历史记录。
- **清理**：删除旧的引用和垃圾回收以完成操作。


___
git remote add origin <remote-repo-url>
git push origin main  -f

