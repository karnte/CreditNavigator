import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import {
  ChevronRight,
  ChevronLeft,
  User,
  DollarSign,
  Home,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";

type FormData = {
  Gender: string;
  Married: string;
  Dependents: string;
  Education: string;
  Self_Employed: string;
  ApplicantIncome: string;
  CoapplicantIncome: string;
  LoanAmount: string;
  Loan_Amount_Term: string;
  Credit_History: string;
  Property_Area: string;
};

const CreditForm = () => {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormData>({
    Gender: "Male",
    Married: "No",
    Dependents: "0",
    Education: "Graduate",
    Self_Employed: "No",
    ApplicantIncome: "",
    CoapplicantIncome: "",
    LoanAmount: "",
    Loan_Amount_Term: "",
    Credit_History: "1",
    Property_Area: "Urban",
  });
  const [result, setResult] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<
    Partial<Record<keyof FormData, boolean>>
  >({});

  const totalSteps = 3;

  const handleChange = (name: keyof FormData, value: string) => {
    setForm((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing/selecting
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: false }));
    }
  };

  // Validate fields for current step
  const validateStep = (currentStep: number): boolean => {
    const newErrors: Partial<Record<keyof FormData, boolean>> = {};

    if (currentStep === 1) {
      // Step 1: All fields have defaults, so they're always valid
      // But we can still check if they're empty strings
      if (!form.Gender) newErrors.Gender = true;
      if (!form.Married) newErrors.Married = true;
      if (!form.Dependents) newErrors.Dependents = true;
      if (!form.Education) newErrors.Education = true;
      if (!form.Self_Employed) newErrors.Self_Employed = true;
    } else if (currentStep === 2) {
      if (!form.ApplicantIncome || form.ApplicantIncome.trim() === "") {
        newErrors.ApplicantIncome = true;
      }
      if (!form.CoapplicantIncome || form.CoapplicantIncome.trim() === "") {
        newErrors.CoapplicantIncome = true;
      }
      if (!form.Credit_History) newErrors.Credit_History = true;
    } else if (currentStep === 3) {
      if (!form.LoanAmount || form.LoanAmount.trim() === "") {
        newErrors.LoanAmount = true;
      }
      if (!form.Loan_Amount_Term) newErrors.Loan_Amount_Term = true;
      if (!form.Property_Area) newErrors.Property_Area = true;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      if (step < totalSteps) setStep(step + 1);
    }
  };

  const handlePrev = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = async () => {
    // Validate all steps before submitting
    const step1Valid = validateStep(1);
    const step2Valid = validateStep(2);
    const step3Valid = validateStep(3);

    if (!step1Valid || !step2Valid || !step3Valid) {
      // Jump to the first step with errors
      if (!step1Valid) setStep(1);
      else if (!step2Valid) setStep(2);
      else if (!step3Valid) setStep(3);
      return;
    }

    setIsLoading(true);

    // Transform frontend data to match backend format
    const backendPayload = {
      Gender: form.Gender,
      Married: form.Married === "Yes" ? "Y" : "N",
      Dependents: parseInt(form.Dependents),
      Education: form.Education === "Graduate" ? "Graduate" : "Undergraduate",
      Self_Employed: form.Self_Employed === "Yes" ? "Y" : "N",
      ApplicantIncome: parseFloat(form.ApplicantIncome),
      CoapplicantIncome: parseFloat(form.CoapplicantIncome || "0"),
      LoanAmount: parseFloat(form.LoanAmount) * 1000, // Convert from thousands
      Loan_Amount_Term: parseFloat(form.Loan_Amount_Term),
      Credit_History: form.Credit_History,
      Property_Area:
        form.Property_Area === "Semiurban" ? "Semi Urban" : form.Property_Area,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(backendPayload),
      });

      if (!response.ok) {
        throw new Error("Prediction failed");
      }

      const data = await response.json();
      setResult(data.prediction);
      setShowResult(true);
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to get prediction. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setForm({
      Gender: "Male",
      Married: "No",
      Dependents: "0",
      Education: "Graduate",
      Self_Employed: "No",
      ApplicantIncome: "",
      CoapplicantIncome: "",
      LoanAmount: "",
      Loan_Amount_Term: "",
      Credit_History: "1",
      Property_Area: "Urban",
    });
    setStep(1);
    setResult(null);
    setShowResult(false);
    setErrors({});
  };

  if (showResult && result !== null) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md p-8 text-center shadow-lg">
          <div className="mb-6">
            {result === 1 ? (
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-success/10 mb-4">
                <CheckCircle2 className="w-12 h-12 text-success" />
              </div>
            ) : (
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-warning/10 mb-4">
                <XCircle className="w-12 h-12 text-warning" />
              </div>
            )}
          </div>

          <h2 className="text-3xl font-bold mb-2">
            {result === 1 ? "Low Credit Risk" : "High Credit Risk"}
          </h2>

          <p className="text-muted-foreground mb-8">
            {result === 1
              ? "Based on the information provided, the applicant shows a favorable credit profile with good repayment probability."
              : "The application indicates elevated risk factors. Additional verification or adjusted terms may be required."}
          </p>

          <div className="space-y-3">
            <Button onClick={resetForm} className="w-full" size="lg">
              Check Another Application
            </Button>
            <Button
              onClick={() => setShowResult(false)}
              variant="outline"
              className="w-full"
              size="lg"
            >
              Review Details
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl p-6 md:p-8 shadow-lg">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Credit Risk Assessment
          </h1>
          <p className="text-muted-foreground">
            Complete the form to evaluate credit eligibility
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-3">
            <span className="text-sm font-medium text-foreground">
              Step {step} of {totalSteps}
            </span>
            <span className="text-sm text-muted-foreground">
              {Math.round((step / totalSteps) * 100)}% Complete
            </span>
          </div>
          <Progress value={(step / totalSteps) * 100} className="h-2" />

          <div className="flex justify-between mt-4">
            <div
              className={`flex items-center gap-2 ${
                step >= 1 ? "text-primary" : "text-muted-foreground"
              }`}
            >
              <User className="w-4 h-4" />
              <span className="text-xs font-medium hidden sm:inline">
                Personal
              </span>
            </div>
            <div
              className={`flex items-center gap-2 ${
                step >= 2 ? "text-primary" : "text-muted-foreground"
              }`}
            >
              <DollarSign className="w-4 h-4" />
              <span className="text-xs font-medium hidden sm:inline">
                Financial
              </span>
            </div>
            <div
              className={`flex items-center gap-2 ${
                step >= 3 ? "text-primary" : "text-muted-foreground"
              }`}
            >
              <Home className="w-4 h-4" />
              <span className="text-xs font-medium hidden sm:inline">
                Loan Details
              </span>
            </div>
          </div>
        </div>

        {/* Step 1: Personal Information */}
        {step === 1 && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="Gender">Gender</Label>
                <Select
                  value={form.Gender}
                  onValueChange={(value) => handleChange("Gender", value)}
                >
                  <SelectTrigger
                    className={cn(
                      errors.Gender && "border-destructive border-2"
                    )}
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Male">Male</SelectItem>
                    <SelectItem value="Female">Female</SelectItem>
                  </SelectContent>
                </Select>
                {errors.Gender && (
                  <p className="text-xs text-destructive">
                    This field is required
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="Married">Marital Status</Label>
                <Select
                  value={form.Married}
                  onValueChange={(value) => handleChange("Married", value)}
                >
                  <SelectTrigger
                    className={cn(
                      errors.Married && "border-destructive border-2"
                    )}
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Yes">Married</SelectItem>
                    <SelectItem value="No">Single</SelectItem>
                  </SelectContent>
                </Select>
                {errors.Married && (
                  <p className="text-xs text-destructive">
                    This field is required
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="Dependents">Number of Dependents</Label>
                <Select
                  value={form.Dependents}
                  onValueChange={(value) => handleChange("Dependents", value)}
                >
                  <SelectTrigger
                    className={cn(
                      errors.Dependents && "border-destructive border-2"
                    )}
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">0</SelectItem>
                    <SelectItem value="1">1</SelectItem>
                    <SelectItem value="2">2</SelectItem>
                    <SelectItem value="3">3+</SelectItem>
                  </SelectContent>
                </Select>
                {errors.Dependents && (
                  <p className="text-xs text-destructive">
                    This field is required
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="Education">Education Level</Label>
                <Select
                  value={form.Education}
                  onValueChange={(value) => handleChange("Education", value)}
                >
                  <SelectTrigger
                    className={cn(
                      errors.Education && "border-destructive border-2"
                    )}
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Graduate">Graduate</SelectItem>
                    <SelectItem value="Not Graduate">Not Graduate</SelectItem>
                  </SelectContent>
                </Select>
                {errors.Education && (
                  <p className="text-xs text-destructive">
                    This field is required
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="Self_Employed">Employment Status</Label>
                <Select
                  value={form.Self_Employed}
                  onValueChange={(value) =>
                    handleChange("Self_Employed", value)
                  }
                >
                  <SelectTrigger
                    className={cn(
                      errors.Self_Employed && "border-destructive border-2"
                    )}
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Yes">Self-Employed</SelectItem>
                    <SelectItem value="No">Employed</SelectItem>
                  </SelectContent>
                </Select>
                {errors.Self_Employed && (
                  <p className="text-xs text-destructive">
                    This field is required
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Financial Information */}
        {step === 2 && (
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="ApplicantIncome">Your Monthly Income (USD)</Label>
              <Input
                id="ApplicantIncome"
                type="number"
                placeholder="e.g., 5000"
                value={form.ApplicantIncome}
                onChange={(e) =>
                  handleChange("ApplicantIncome", e.target.value)
                }
                className={cn(
                  errors.ApplicantIncome && "border-destructive border-2"
                )}
              />
              {errors.ApplicantIncome ? (
                <p className="text-xs text-destructive">
                  This field is required
                </p>
              ) : (
                <p className="text-xs text-muted-foreground">
                  Enter your total monthly income before taxes
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="CoapplicantIncome">
                Co-applicant Monthly Income (USD)
              </Label>
              <Input
                id="CoapplicantIncome"
                type="number"
                placeholder="e.g., 3000 (or 0 if none)"
                value={form.CoapplicantIncome}
                onChange={(e) =>
                  handleChange("CoapplicantIncome", e.target.value)
                }
                className={cn(
                  errors.CoapplicantIncome && "border-destructive border-2"
                )}
              />
              {errors.CoapplicantIncome ? (
                <p className="text-xs text-destructive">
                  This field is required
                </p>
              ) : (
                <p className="text-xs text-muted-foreground">
                  Enter 0 if there is no co-applicant
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="Credit_History">Credit History</Label>
              <Select
                value={form.Credit_History}
                onValueChange={(value) => handleChange("Credit_History", value)}
              >
                <SelectTrigger
                  className={cn(
                    errors.Credit_History && "border-destructive border-2"
                  )}
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Good - Meets guidelines</SelectItem>
                  <SelectItem value="0">
                    Poor - Does not meet guidelines
                  </SelectItem>
                </SelectContent>
              </Select>
              {errors.Credit_History ? (
                <p className="text-xs text-destructive">
                  This field is required
                </p>
              ) : (
                <p className="text-xs text-muted-foreground">
                  Select based on previous credit performance
                </p>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Loan Details */}
        {step === 3 && (
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="LoanAmount">Loan Amount (in thousands)</Label>
              <Input
                id="LoanAmount"
                type="number"
                placeholder="e.g., 150 (for $150,000)"
                value={form.LoanAmount}
                onChange={(e) => handleChange("LoanAmount", e.target.value)}
                className={cn(
                  errors.LoanAmount && "border-destructive border-2"
                )}
              />
              {errors.LoanAmount ? (
                <p className="text-xs text-destructive">
                  This field is required
                </p>
              ) : (
                <p className="text-xs text-muted-foreground">
                  Enter the amount in thousands (e.g., 150 for $150,000)
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="Loan_Amount_Term">Loan Term (months)</Label>
              <Select
                value={form.Loan_Amount_Term}
                onValueChange={(value) =>
                  handleChange("Loan_Amount_Term", value)
                }
              >
                <SelectTrigger
                  className={cn(
                    errors.Loan_Amount_Term && "border-destructive border-2"
                  )}
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="360">360 months (30 years)</SelectItem>
                  <SelectItem value="240">240 months (20 years)</SelectItem>
                  <SelectItem value="180">180 months (15 years)</SelectItem>
                  <SelectItem value="120">120 months (10 years)</SelectItem>
                </SelectContent>
              </Select>
              {errors.Loan_Amount_Term && (
                <p className="text-xs text-destructive">
                  This field is required
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="Property_Area">Property Location</Label>
              <Select
                value={form.Property_Area}
                onValueChange={(value) => handleChange("Property_Area", value)}
              >
                <SelectTrigger
                  className={cn(
                    errors.Property_Area && "border-destructive border-2"
                  )}
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Urban">Urban</SelectItem>
                  <SelectItem value="Semiurban">Semiurban</SelectItem>
                  <SelectItem value="Rural">Rural</SelectItem>
                </SelectContent>
              </Select>
              {errors.Property_Area && (
                <p className="text-xs text-destructive">
                  This field is required
                </p>
              )}
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8 gap-4">
          <Button
            variant="outline"
            onClick={handlePrev}
            disabled={step === 1}
            className="flex items-center gap-2"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </Button>

          {step < totalSteps ? (
            <Button onClick={handleNext} className="flex items-center gap-2">
              Next
              <ChevronRight className="w-4 h-4" />
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              {isLoading ? "Calculating..." : "Calculate Risk"}
              {!isLoading && <ChevronRight className="w-4 h-4" />}
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
};

export default CreditForm;
