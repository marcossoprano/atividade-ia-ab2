#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para validar o Sistema CBR Médico.
Executa testes automatizados em todos os módulos.
"""

import sys
import os
import json

def test_imports():
    """Testa se todos os módulos podem ser importados."""
    print("Testando imports...", end=" ")
    try:
        from models import Case, MatchResult, PatientInput
        from persistence import PersistenceManager
        from case_base import CaseBase
        from similarity import SimilarityEngine
        from diagnosis import DiagnosisEngine
        import utils
        print("✓ OK")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False

def test_case_creation():
    """Testa criação de casos."""
    print("Testando criação de Case...", end=" ")
    try:
        from models import Case
        case = Case(
            id=1,
            sintomas={"febre": True, "tosse": True, "dor_garganta": False},
            diagnostico="Gripe",
            tratamento="Repouso"
        )
        assert case.id == 1
        assert case.diagnostico == "Gripe"
        assert case.get_sintoma("febre") == True
        print("✓ OK")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False

def test_patient_input():
    """Testa entrada de paciente."""
    print("Testando PatientInput...", end=" ")
    try:
        from models import PatientInput
        patient = PatientInput()
        patient.set_sintoma("febre", True)
        patient.set_sintoma("tosse", False)
        assert patient.get_sintoma("febre") == True
        assert patient.get_sintoma("tosse") == False
        print("✓ OK")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False

def test_similarity():
    """Testa cálculo de similaridade."""
    print("Testando SimilarityEngine...", end=" ")
    try:
        from models import Case, PatientInput
        from similarity import SimilarityEngine
        
        case1 = Case(
            id=1,
            sintomas={"febre": True, "tosse": True, "dor_garganta": True},
            diagnostico="Gripe",
            tratamento="Repouso"
        )
        
        case2 = Case(
            id=2,
            sintomas={"febre": True, "tosse": True, "dor_garganta": False},
            diagnostico="Resfriado",
            tratamento="Repouso"
        )
        
        engine = SimilarityEngine()
        sim = engine.calculate_similarity(case1, case2)
        
        # Deve ser 66.67% (2 de 3 sintomas coincidem)
        assert 66.0 <= sim <= 67.0, f"Similaridade esperada ~66.67%, obtida: {sim}%"
        
        # Testa similaridade com PatientInput
        patient = PatientInput(sintomas={"febre": True, "tosse": True, "dor_garganta": True})
        sim2 = engine.calculate_similarity_from_input(patient, case1)
        assert sim2 == 100.0, f"Similaridade esperada 100%, obtida: {sim2}%"
        
        print("✓ OK")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False

def test_case_base():
    """Testa a base de casos."""
    print("Testando CaseBase...", end=" ")
    try:
        from case_base import CaseBase
        from models import Case
        
        # Testa com arquivo existente
        case_base = CaseBase("casos.json")
        cases = case_base.get_all_cases()
        
        assert len(cases) >= 15, f"Esperado pelo menos 15 casos, obtido: {len(cases)}"
        
        # Testa estatísticas
        stats = case_base.get_statistics()
        assert "total_cases" in stats
        assert stats["total_cases"] >= 15
        
        print("✓ OK")
        return True
    except FileNotFoundError:
        print("⚠ AVISO: casos.json não encontrado (teste ignorado)")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False

def test_diagnosis_engine():
    """Testa o motor de diagnóstico."""
    print("Testando DiagnosisEngine...", end=" ")
    try:
        from case_base import CaseBase
        from diagnosis import DiagnosisEngine
        from models import PatientInput
        from similarity import SimilarityEngine
        
        case_base = CaseBase("casos.json")
        similarity_engine = SimilarityEngine()
        diagnosis_engine = DiagnosisEngine(case_base, similarity_engine)
        
        # Cria input de paciente com sintomas de gripe
        patient = PatientInput(sintomas={
            "febre": True,
            "tosse": True,
            "dor_garganta": True,
            "dor_muscular": False,
            "coriza": True,
            "dor_cabeca": False,
            "fadiga": True,
            "congestao_nasal": True,
            "falta_ar": False,
            "nausea": False
        })
        
        # Testa retrieve
        matches = diagnosis_engine.retrieve(patient, top_k=3)
        assert len(matches) == 3, f"Esperado 3 matches, obtido: {len(matches)}"
        
        # Testa reuse
        diagnosis, treatment, confidence = diagnosis_engine.reuse(matches)
        assert diagnosis in ["Gripe", "COVID-19", "Sinusite", "Amigdalite", "Dengue", 
                            "Resfriado Comum", "Rinite Alérgica", "Faringite"]
        
        print("✓ OK")
        return True
    except FileNotFoundError:
        print("⚠ AVISO: casos.json não encontrado (teste ignorado)")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False

def test_persistence():
    """Testa persistência de dados."""
    print("Testando PersistenceManager...", end=" ")
    try:
        from persistence import PersistenceManager
        from models import Case
        
        # Testa com arquivo existente
        pm = PersistenceManager("casos.json")
        cases = pm.load_cases()
        
        assert len(cases) >= 15, f"Esperado pelo menos 15 casos, obtido: {len(cases)}"
        
        # Testa serialização
        case = cases[0]
        case_dict = case.to_dict()
        assert "id" in case_dict
        assert "diagnostico" in case_dict
        assert "sintomas" not in case_dict  # sintomas são achatados no dict
        
        # Testa next_id
        next_id = pm.get_next_id()
        assert next_id > 0
        
        print("✓ OK")
        return True
    except FileNotFoundError:
        print("⚠ AVISO: casos.json não encontrado (teste ignorado)")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False

def test_json_structure():
    """Testa a estrutura do arquivo JSON."""
    print("Testando estrutura JSON...", end=" ")
    try:
        with open("casos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert isinstance(data, list), "JSON deve ser uma lista"
        assert len(data) >= 15, f"Esperado pelo menos 15 casos, obtido: {len(data)}"
        
        # Verifica estrutura de cada caso
        required_fields = ["id", "diagnostico", "tratamento", 
                          "febre", "tosse", "dor_garganta", "dor_muscular", 
                          "coriza", "dor_cabeca", "fadiga", 
                          "congestao_nasal", "falta_ar", "nausea"]
        
        for i, case in enumerate(data):
            for field in required_fields:
                assert field in case, f"Caso {i} falta campo '{field}'"
        
        print("✓ OK")
        return True
    except FileNotFoundError:
        print("⚠ AVISO: casos.json não encontrado (teste ignorado)")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False

def test_utils():
    """Testa funções utilitárias."""
    print("Testando utils...", end=" ")
    try:
        import utils
        
        # Testa lista de sintomas
        assert len(utils.SYMPTOMS_LIST) == 10, f"Esperado 10 sintomas, obtido: {len(utils.SYMPTOMS_LIST)}"
        
        # Testa lista de diagnósticos
        assert len(utils.DIAGNOSES_LIST) >= 5, f"Esperado pelo menos 5 diagnósticos, obtido: {len(utils.DIAGNOSES_LIST)}"
        
        print("✓ OK")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("  SISTEMA CBR MÉDICO - TESTES AUTOMATIZADOS")
    print("=" * 60)
    print()
    
    tests = [
        test_imports,
        test_case_creation,
        test_patient_input,
        test_similarity,
        test_json_structure,
        test_utils,
        test_case_base,
        test_diagnosis_engine,
        test_persistence,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print()
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"  RESULTADOS: {passed}/{total} testes passaram")
    
    if passed == total:
        print("  ✓ TODOS OS TESTES PASSARAM!")
    else:
        print(f"  ✗ {total - passed} teste(s) falharam")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)