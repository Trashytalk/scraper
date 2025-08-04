#!/usr/bin/env python3
"""
Configuration Validation Script
Validates all configuration files and system readiness
"""

import asyncio
import os
import sys


async def validate_configuration():
    """Validate the configuration system"""
    try:
        from config.advanced_config_manager import ConfigManager, init_config

        # Test development config
        if os.path.exists("config/development.yaml"):
            config = await init_config("config/development.yaml", "development")
            print("✅ Development configuration valid")
            print(f"   Database: {config.database.url}")
            print(f"   Redis: {config.redis.host}:{config.redis.port}")
            return True
        else:
            print("❌ Development configuration file not found")
            return False

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


async def validate_monitoring():
    """Validate the monitoring system"""
    try:
        from monitoring.simple_health_monitor import SimpleHealthMonitor

        monitor = SimpleHealthMonitor("data.db")
        health = await monitor.comprehensive_health_check()

        print("✅ Health monitoring system functional")
        print(f"   Status: {health['status']}")
        print(f"   System checks: {len(health['checks'])}")
        return True

    except Exception as e:
        print(f"❌ Monitoring validation failed: {e}")
        return False


async def main():
    """Main validation function"""
    print("🧪 Phase 1 System Validation")
    print("============================")

    config_ok = await validate_configuration()
    monitoring_ok = await validate_monitoring()

    if config_ok and monitoring_ok:
        print("\n✅ All systems validated successfully!")
        print("🚀 Ready to start enhanced server with: ./start_enhanced_server.sh")
        return 0
    else:
        print("\n❌ Validation failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
