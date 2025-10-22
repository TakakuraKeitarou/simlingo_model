# %%
import os
import subprocess
import time
import ujson
import shutil
from tqdm.autonotebook import tqdm

# %%
def run_bench2drive_evaluation(job, port, tm_port):
    """Bench2Driveの評価を実行する関数"""
    cfg = job["cfg"]
    route = job["route"]
    route_id = job["route_id"]
    seed = job["seed"]
    viz_path = job["viz_path"]
    result_file = job["result_file"]
    log_file = job["log_file"]
    err_file = job["err_file"]

    # 環境変数の設定
    env = os.environ.copy()
    
    # PYTHONPATHを正しく設定
    python_paths = [
        cfg["repo_root"],
        f"{cfg['repo_root']}/team_code",
        f"{cfg['carla_root']}/PythonAPI/carla",
        f"{cfg['repo_root']}/Bench2Drive",
        f"{cfg['repo_root']}/Bench2Drive/scenario_runner",
        f"{cfg['repo_root']}/Bench2Drive/leaderboard",
    ]
    
    # 既存のPYTHONPATHがあれば追加
    if 'PYTHONPATH' in env:
        existing_paths = env['PYTHONPATH'].split(':')
        for path in existing_paths:
            if path and path not in python_paths:
                python_paths.append(path)
    
    # 環境変数を更新
    env.update({
        'CARLA_ROOT': cfg['carla_root'],
        'WORK_DIR': cfg['repo_root'],
        'PYTHONPATH': ':'.join(python_paths),
        'SCENARIO_RUNNER_ROOT': f"{cfg['repo_root']}/Bench2Drive/scenario_runner",
        'LEADERBOARD_ROOT': f"{cfg['repo_root']}/Bench2Drive/leaderboard",
        'SAVE_PATH': viz_path,
        'TEAM_CODE_ROOT': f"{cfg['repo_root']}/team_code",
    })
    
    # デバッグ用：環境変数をログに出力
    with open(log_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write(f"JOB CONFIGURATION\n")
        f.write("="*70 + "\n")
        f.write(f"JOB ID: local_{route_id}_{seed}\n")
        f.write(f"Agent: {cfg['agent']}\n")
        f.write(f"Checkpoint: {cfg['checkpoint']}\n")
        f.write(f"Route: {route}\n")
        f.write("-"*70 + "\n")
        f.write("ENVIRONMENT VARIABLES:\n")
        f.write("-"*70 + "\n")
        f.write(f"CARLA_ROOT: {env['CARLA_ROOT']}\n")
        f.write(f"WORK_DIR: {env['WORK_DIR']}\n")
        f.write(f"TEAM_CODE_ROOT: {env['TEAM_CODE_ROOT']}\n")
        f.write(f"SCENARIO_RUNNER_ROOT: {env['SCENARIO_RUNNER_ROOT']}\n")
        f.write(f"LEADERBOARD_ROOT: {env['LEADERBOARD_ROOT']}\n")
        f.write(f"SAVE_PATH: {env['SAVE_PATH']}\n")
        f.write("\nPYTHONPATH entries:\n")
        for i, path in enumerate(python_paths, 1):
            f.write(f"  {i}. {path}\n")
            # パスが存在するかチェック
            if os.path.exists(path):
                f.write(f"     ✓ Path exists\n")
            else:
                f.write(f"     ✗ Path NOT found\n")
        f.write("-"*70 + "\n")

    # コマンドの構築
    cmd = [
        'python', '-u', 
        f"{cfg['repo_root']}/Bench2Drive/leaderboard/leaderboard/leaderboard_evaluator.py",
        f'--routes={route}',
        '--repetitions=1',
        '--track=SENSORS',
        f'--checkpoint={result_file}',
        '--timeout=600',
        f"--agent={cfg['agent_file']}",
        f"--agent-config={cfg['checkpoint']}",
        f'--traffic-manager-seed={seed}',
        f'--port={port}',
        f'--traffic-manager-port={tm_port}'
    ]

    print(f"\n{'='*60}")
    print(f"実行開始: {cfg['agent']}_{seed}_{cfg['benchmark']}_{route_id}")
    print(f"作業ディレクトリ: {cfg['repo_root']}")
    print(f"エージェントファイル: {cfg['agent_file']}")
    print(f"{'='*60}\n")
    
    # 重要なファイルの存在確認
    important_files = [
        cfg['agent_file'],
        f"{cfg['repo_root']}/team_code/__init__.py",
        f"{cfg['repo_root']}/team_code/config_simlingo.py",
        f"{cfg['repo_root']}/simlingo_training/__init__.py",
    ]
    
    for file_path in important_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - ファイルが見つかりません！")
    
    try:
        # ログファイルを開く（追記モード）
        with open(log_file, 'a') as log_f, open(err_file, 'w') as err_f:
            log_f.write("\nCOMMAND:\n")
            log_f.write(' '.join(cmd) + "\n")
            log_f.write("="*70 + "\n\n")
            log_f.write("OUTPUT:\n")
            log_f.write("-"*70 + "\n")
            log_f.flush()
            
            # プロセスを実行
            process = subprocess.run(
                cmd,
                cwd=cfg["repo_root"],
                env=env,
                stdout=log_f,
                stderr=err_f,
                timeout=3*60*60,  # 3時間のタイムアウト
                check=False
            )
            
            # 終了コードをチェック
            if process.returncode == 0:
                print(f"✓ 正常完了: {cfg['agent']}_{seed}_{cfg['benchmark']}_{route_id}")
                return True
            else:
                print(f"✗ エラー終了 (終了コード: {process.returncode})")
                print(f"   {cfg['agent']}_{seed}_{cfg['benchmark']}_{route_id}")
                
                # エラー内容を読み込んで表示
                try:
                    with open(err_file, 'r') as err_read:
                        error_content = err_read.read()
                        if error_content:
                            print("\n--- エラー内容（最初の1000文字）---")
                            print(error_content[:1000])
                            print("--- エラー内容ここまで ---\n")
                            
                            # エラーファイルに追記
                            with open(err_file, 'a') as err_append:
                                err_append.write(f"\n{'='*70}\n")
                                err_append.write(f"Process exited with code: {process.returncode}\n")
                                err_append.write(f"{'='*70}\n")
                except:
                    pass
                    
                return False
        
    except subprocess.TimeoutExpired:
        print(f"⏱ タイムアウト (3時間): {cfg['agent']}_{seed}_{cfg['benchmark']}_{route_id}")
        with open(err_file, 'a') as err_f:
            err_f.write("\n\n" + "="*70 + "\n")
            err_f.write("TIMEOUT: Process killed after 3 hours\n")
            err_f.write("="*70 + "\n")
        return False
        
    except Exception as e:
        print(f"⚠ 予期しないエラー: {cfg['agent']}_{seed}_{cfg['benchmark']}_{route_id}")
        print(f"  エラー詳細: {str(e)}")
        
        with open(err_file, 'a') as err_f:
            err_f.write("\n\n" + "="*70 + "\n")
            err_f.write(f"UNEXPECTED ERROR: {str(e)}\n")
            err_f.write("="*70 + "\n")
            import traceback
            err_f.write("Traceback:\n")
            err_f.write(traceback.format_exc())
            
        return False

# %%
def filter_completed(jobs):
    """完了したジョブをフィルタリング"""
    filtered_jobs = []

    for job in jobs:
        result_file = job["result_file"]
        if os.path.exists(result_file):
            try:
                with open(result_file, "r") as f:
                    evaluation_data = ujson.load(f)
            except:
                if job["tries"] > 0:
                    filtered_jobs.append(job)
                    continue

            progress = evaluation_data['_checkpoint']['progress']

            need_to_resubmit = False
            if len(progress) < 2 or progress[0] < progress[1]:
                need_to_resubmit = True
            else:
                for record in evaluation_data['_checkpoint']['records']:
                    if record['status'] in ['Failed - Agent couldn\'t be set up', 'Failed', 'Failed - Simulation crashed', 'Failed - Agent crashed']:
                        need_to_resubmit = True

            if need_to_resubmit and job["tries"] > 0:
                filtered_jobs.append(job)
        elif job["tries"] > 0:
            filtered_jobs.append(job)
            
    return filtered_jobs

# %%
def load_config():
    """環境変数から設定を読み込む（デフォルト値付き）"""
    # リポジトリルートを取得（このスクリプトがrepo_root直下にあると仮定）
    default_repo_root = os.path.dirname(os.path.abspath(__file__))
    
    repo_root = os.environ.get('REPO_ROOT', default_repo_root)
    carla_root = os.environ.get('CARLA_ROOT', '/path/to/carla')
    
    configs = [
        {
            "agent": "simlingo",
            "checkpoint": "simlingo/checkpoints/epoch=013.ckpt/pytorch_model.pt",
            "benchmark": "bench2drive",
            "route_path": os.path.join(repo_root, "leaderboard/data/bench2drive_split"),
            "seeds": [1, 2, 3],
            "tries": 2,
            "out_root": "eval_results/Bench2Drive",
            "carla_root": carla_root,
            "repo_root": repo_root,
            "agent_file": os.path.join(repo_root, "team_code/agent_simlingo.py"),
            "team_code": "team_code",
            "agent_config": "not_used"
        }
    ]
    
    return configs

# %%
if __name__ == "__main__":
    # 設定の読み込み
    configs = load_config()
    
    # ジョブキューの作成
    job_queue = []
    for cfg_idx, cfg in enumerate(configs):
        route_path = cfg["route_path"]
        routes = [x for x in os.listdir(route_path) if x[-4:] == ".xml"]

        if cfg["benchmark"] == "bench2drive":
            fill_zeros = 3
        else: 
            fill_zeros = 2

        for seed in cfg["seeds"]:
            seed = str(seed)

            base_dir = os.path.join(cfg["out_root"], cfg["agent"], cfg["benchmark"], seed)
            os.makedirs(os.path.join(base_dir, "run"), exist_ok=True)
            os.makedirs(os.path.join(base_dir, "res"), exist_ok=True)
            os.makedirs(os.path.join(base_dir, "out"), exist_ok=True)
            os.makedirs(os.path.join(base_dir, "err"), exist_ok=True)

            for route in routes:
                route_id = route.split("_")[-1][:-4].zfill(fill_zeros)
                route = os.path.join(route_path, route)

                viz_path = os.path.join(base_dir, "viz", route_id)
                os.makedirs(viz_path, exist_ok=True)

                result_file = os.path.join(base_dir, "res", f"{route_id}_res.json")
                log_file = os.path.join(base_dir, "out", f"{route_id}_out.log")
                err_file = os.path.join(base_dir, "err", f"{route_id}_err.log")
                
                job = {
                    "cfg": cfg,
                    "route": route,
                    "route_id": route_id,
                    "seed": seed,
                    "viz_path": viz_path,
                    "result_file": result_file,
                    "log_file": log_file,
                    "err_file": err_file,
                    "tries": cfg["tries"]
                }

                job_queue.append(job)

    # ポート設定
    carla_world_port = 10000
    carla_tm_port = 8000

    # ジョブの実行
    jobs = len(job_queue)
    progress = tqdm(total=jobs)

    while job_queue:
        job_queue = filter_completed(job_queue)
        progress.update(jobs - len(job_queue) - progress.n)
        
        if not job_queue:
            break

        for job in job_queue:
            if job["tries"] <= 0:
                continue

            # vizディレクトリをクリーンアップ
            if os.path.exists(job["viz_path"]):
                shutil.rmtree(job["viz_path"])
            os.makedirs(job["viz_path"], exist_ok=True)

            # Bench2Drive評価の実行
            if job["cfg"]["benchmark"].lower() == "bench2drive":
                success = run_bench2drive_evaluation(job, carla_world_port, carla_tm_port)
            else:
                raise NotImplementedError(f"Benchmark {job['cfg']['benchmark']} not implemented.")

            job["tries"] -= 1
            
            if success:
                print(f'完了: {job["route_id"]}')
            else:
                print(f'失敗: {job["route_id"]} (残り試行回数: {job["tries"]})')
            
            time.sleep(2)
            break

        time.sleep(1)

    progress.close()
    print("すべてのジョブが完了しました。")