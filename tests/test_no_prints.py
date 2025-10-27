"""
Test para verificar ausencia de prints en código de producción.
"""
import os
import re
import pytest


def test_no_print_statements_in_production_code():
    """
    Issue #1 - Correctivo:
    Verifica que no haya statements print() en código de producción.
    
    Este test busca prints en archivos Python críticos y falla si encuentra alguno.
    """
    # Archivos a verificar (código de producción, no scripts de migración)
    production_files = [
        'app.py',
        'models.py',
        'services/analytics_service.py',
        'services/auth_service.py',
        'services/session_service.py',
        'repositories/session_repository.py',
        'repositories/profesor_repository.py',
        'repositories/estudiante_repository.py',
        'utils/decorators.py',
        'utils/validators.py',
        'data_analytics.py'
    ]
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    files_with_prints = []
    
    for file_path in production_files:
        full_path = os.path.join(project_root, file_path)
        
        if not os.path.exists(full_path):
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar print() pero ignorar comentarios y strings
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Ignorar comentarios
            if line.strip().startswith('#'):
                continue
            
            # Buscar print( pero no en docstrings
            if re.search(r'\bprint\s*\(', line):
                # Verificar que no sea parte de un string o comentario
                if not (line.strip().startswith('"""') or line.strip().startswith("'''")):
                    files_with_prints.append(f"{file_path}:{line_num}")
    
    # Assertion con mensaje claro
    assert len(files_with_prints) == 0, (
        f"\n❌ Encontrados {len(files_with_prints)} statements print() en código de producción:\n" +
        "\n".join(f"  - {f}" for f in files_with_prints) +
        "\n\n💡 Reemplaza print() por logging.debug(), logging.info(), etc."
    )


def test_logging_is_configured():
    """Verifica que el sistema de logging esté configurado."""
    import app as app_module
    
    # Verificar que logging está importado
    assert hasattr(app_module, 'logging') or hasattr(app_module, 'logger'), (
        "❌ El módulo app.py debe importar y configurar logging"
    )


def test_no_debug_print_in_routes():
    """
    Verifica específicamente que las rutas de Flask no tengan prints de debug.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_file = os.path.join(project_root, 'app.py')
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar patrones comunes de debug prints
    debug_patterns = [
        r'print\("DEBUG',
        r'print\(f"DEBUG',
        r'print\("🔵',  # Emoji debug prints
        r'print\(f"🔵',
        r'print\("❌',  # Error prints
        r'print\(f"❌',
        r'print\("📊',  # Stats prints
        r'print\(f"📊',
    ]
    
    found_patterns = []
    for pattern in debug_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Get line number
            line_num = content[:match.start()].count('\n') + 1
            found_patterns.append(f"Line {line_num}: {pattern}")
    
    assert len(found_patterns) == 0, (
        f"\n❌ Encontrados {len(found_patterns)} prints de debug en app.py:\n" +
        "\n".join(f"  - {p}" for p in found_patterns)
    )
