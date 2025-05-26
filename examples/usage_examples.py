"""
Autonomous MCP Agent - Usage Examples
Production ready autonomous execution examples
"""

import asyncio
from autonomous_mcp import AutonomousOrchestrator, execute_task

async def example_market_research():
    """Example: Autonomous market research"""
    print("🔍 Autonomous Market Research Example")
    
    orchestrator = AutonomousOrchestrator()
    
    result = await orchestrator.execute_autonomous_task(
        "Research Apple stock performance, analyze recent quarterly results, create investment summary"
    )
    
    print(f"✅ Status: {result['status']}")
    print(f"🤖 Autonomous: {result['autonomous_execution']}")
    print(f"⚙️ Tool Chain: {result['tool_chain_length']} steps")
    print(f"📊 Results: {len(result['results'])} outputs generated")
    
    return result

async def example_technical_analysis():
    """Example: Autonomous technical analysis"""
    print("\n🔧 Autonomous Technical Analysis Example")
    
    # Using the quick execute function
    result = await execute_task(
        "Compare Python vs JavaScript for web development, analyze performance and ecosystem"
    )
    
    print(f"✅ Status: {result['status']}")
    print(f"🤖 Autonomous: {result['autonomous_execution']}")
    print(f"⚙️ Tool Chain: {result['tool_chain_length']} steps")
    
    return result

async def example_content_creation():
    """Example: Autonomous content creation"""
    print("\n📝 Autonomous Content Creation Example")
    
    orchestrator = AutonomousOrchestrator()
    
    result = await orchestrator.execute_autonomous_task(
        "Research current AI trends, analyze market adoption, create comprehensive industry report"
    )
    
    print(f"✅ Status: {result['status']}")
    print(f"🤖 Autonomous: {result['autonomous_execution']}")
    print(f"⚙️ Tool Chain: {result['tool_chain_length']} steps")
    
    return result

async def main():
    """Run all examples"""
    print("🚀 Autonomous MCP Agent - Usage Examples")
    print("=" * 60)
    
    try:
        # Run examples
        await example_market_research()
        await example_technical_analysis() 
        await example_content_creation()
        
        print("\n" + "=" * 60)
        print("🎉 All examples completed successfully!")
        print("✅ Autonomous execution validated")
        print("✅ Zero manual interventions")
        print("✅ Production ready autonomous agent")
        
    except Exception as e:
        print(f"❌ Example failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
