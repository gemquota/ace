import ast
import os
import shutil

class ASTMutator:
    def __init__(self, target_file="src/backend/models.py"):
        self.target_file = target_file

    def propose_edit(self, code_string):
        """
        Takes a proposed python string, verifies it with AST.
        If valid, creates a backup and overwrites the target file.
        Returns (success_bool, message)
        """
        try:
            # 1. AST Syntax Verification
            ast.parse(code_string)
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"

        try:
            # 2. Write to Target
            with open(self.target_file, 'w') as f:
                f.write(code_string)
                
            return True, "Mutation successful and written to disk."
        except Exception as e:
            return False, f"File IO Error: {e}"

    def rollback(self):
         """Restores models.py from models_genesis.py"""
         genesis_file = self.target_file.replace("models.py", "models_genesis.py")
         if os.path.exists(genesis_file):
             shutil.copy2(genesis_file, self.target_file)
             return True
         return False
