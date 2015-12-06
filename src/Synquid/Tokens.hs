-- | Lexems of the Synquid language
module Synquid.Tokens where

import Synquid.Logic
import Data.Map (Map, fromList)

-- | Keywords
keywords :: [String]
keywords = ["Bool", "data", "decreases", "False", "in", "Int", "match", "measure", "predicate", "qualifier", "Set", "True", "type", "where"]

-- | Names of unary operators    
unOpTokens :: Map UnOp String
unOpTokens = fromList [ (Neg, "-")
                      , (Not, "!")
                      , (Abs, "~")
                      ]
                           
-- | Names of binary operators             
binOpTokens :: Map BinOp String
binOpTokens = fromList [ (Times,     "*")
                       , (Plus,      "+")
                       , (Minus,     "-")
                       , (Eq,        "==")
                       , (Neq,       "!=")
                       , (Lt,        "<")
                       , (Le,        "<=")
                       , (Gt,        ">")
                       , (Ge,        ">=")
                       , (And,       "&&")
                       , (Or,        "||")
                       , (Implies,   "==>")
                       , (Iff,       "<==>")
                       , (Union,     "+")
                       , (Intersect, "*")
                       , (Diff,      "-")
                       , (Member,    "in")
                       , (Subset,    "<=")
                       ]
                        
-- | Other operators         
otherOps :: [String]
otherOps = ["::", ":", "->", "|", "=", "??", ",", "."] 

-- | Characters allowed in identifiers (in addition to letters and digits)
identifierChars = "_'"
-- | Start of a multi-line comment
commentStart = "{-"
-- | End of a multi-line comment
commentEnd = "-}"
-- | Start of a single-line comment
commentLine = "--"