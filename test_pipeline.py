"""
Test del pipeline sin Flow ni email
"""
import asyncio
import sys
from dotenv import load_dotenv
from pipeline import run_pipeline

load_dotenv()

async def test():
    pedido = {
        "tipo": "due_diligence",
        "objetivo": "Empresa Falabella S.A. RUT 99.534.920-1",
        "email": "test@test.com",
        "nombre": "Joaquin",
        "datos_extra": ""
    }

    print(f"\n🚀 Iniciando test con pedido:")
    print(f"  - Tipo: {pedido['tipo']}")
    print(f"  - Objetivo: {pedido['objetivo']}")
    print(f"  - Nombre: {pedido['nombre']}\n")

    try:
        await run_pipeline(pedido)
        print("\n✅ Test completado exitosamente")
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test())
