#!/usr/bin/env python
"""
Quick start script for training and running the API locally
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command"""
    print(f"\n> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result


def train_model(smoke=False):
    """Train the model"""
    print("\n" + "=" * 60)
    print("🎯 TRAINING MODEL")
    print("=" * 60)

    cmd = ["python", "train.py"]
    if smoke:
        cmd.extend(["--smoke", "--k-folds", "3"])

    run_command(cmd, cwd="src")

    print("\n✅ Training complete!")
    print("📊 View results: mlflow ui")


def start_mlflow():
    """Start MLflow UI"""
    print("\n" + "=" * 60)
    print("📊 STARTING MLFLOW UI")
    print("=" * 60)
    print("Opening MLflow UI at http://localhost:5000")
    print("Press Ctrl+C to stop")

    run_command(["mlflow", "ui", "--backend-store-uri", "file:./src/mlruns"])


def start_api():
    """Start the FastAPI server"""
    print("\n" + "=" * 60)
    print("🚀 STARTING API SERVER")
    print("=" * 60)

    # Check if model exists
    model_path = Path("models/latest/model")
    if not model_path.exists():
        print("\n⚠️  No model found at models/latest/model")
        print("   Would you like to train a model first? (y/n)")
        response = input("> ")
        if response.lower() == 'y':
            train_model(smoke=True)
        else:
            print("❌ Cannot start API without a trained model")
            sys.exit(1)

    print("\n🚀 Starting FastAPI server...")
    print("📖 API docs: http://localhost:8000/docs")
    print("🏥 Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop")

    os.chdir("src")
    run_command(["uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])


def run_tests():
    """Run tests"""
    print("\n" + "=" * 60)
    print("🧪 RUNNING TESTS")
    print("=" * 60)

    run_command(["pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing"])

    print("\n✅ Tests complete!")


def docker_up():
    """Start Docker Compose services"""
    print("\n" + "=" * 60)
    print("🐳 STARTING DOCKER SERVICES")
    print("=" * 60)

    run_command(["docker-compose", "up", "-d"])

    print("\n✅ Services started!")
    print("📊 MLflow UI: http://localhost:5000")
    print("🚀 API: http://localhost:8000")
    print("\nTo stop: python run.py docker-down")


def docker_down():
    """Stop Docker Compose services"""
    print("\n" + "=" * 60)
    print("🐳 STOPPING DOCKER SERVICES")
    print("=" * 60)

    run_command(["docker-compose", "down"])

    print("\n✅ Services stopped!")


def main():
    parser = argparse.ArgumentParser(
        description="Breast Cancer ML Pipeline - Quick Start Script"
    )

    parser.add_argument(
        "command",
        choices=["train", "train-smoke", "mlflow", "api", "test", "docker-up", "docker-down", "all"],
        help="Command to run"
    )

    args = parser.parse_args()

    if args.command == "train":
        train_model(smoke=False)

    elif args.command == "train-smoke":
        train_model(smoke=True)

    elif args.command == "mlflow":
        start_mlflow()

    elif args.command == "api":
        start_api()

    elif args.command == "test":
        run_tests()

    elif args.command == "docker-up":
        docker_up()

    elif args.command == "docker-down":
        docker_down()

    elif args.command == "all":
        print("\n🚀 Running full pipeline...\n")
        train_model(smoke=False)
        print("\n✅ Training complete! Starting API...")
        input("\nPress Enter to start API server...")
        start_api()


if __name__ == "__main__":
    main()
