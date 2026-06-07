(function () {
  if (window.__maridavSiteCrmBridgeLoaded) {
    return;
  }
  window.__maridavSiteCrmBridgeLoaded = true;

  var ENDPOINTS = {
    inbound: "/api/v1/public/inbound/",
    careers: "/api/v1/public/careers/",
    newsletter: "/api/v1/public/newsletter/",
  };

  function getUrlParams() {
    var url = new URL(window.location.href);
    return {
      utm_source: url.searchParams.get("utm_source") || "",
      utm_medium: url.searchParams.get("utm_medium") || "",
      utm_campaign: url.searchParams.get("utm_campaign") || "",
      utm_content: url.searchParams.get("utm_content") || "",
      utm_term: url.searchParams.get("utm_term") || "",
    };
  }

  function basePayload() {
    var utm = getUrlParams();
    return {
      source_page: window.location.href,
      referrer: document.referrer || "",
      utm_source: utm.utm_source,
      utm_medium: utm.utm_medium,
      utm_campaign: utm.utm_campaign,
      utm_content: utm.utm_content,
      utm_term: utm.utm_term,
      user_agent: navigator.userAgent || "",
    };
  }

  function firstValue(formData, names) {
    for (var i = 0; i < names.length; i += 1) {
      var value = formData.get(names[i]);
      if (value !== null && String(value).trim() !== "") {
        return String(value).trim();
      }
    }
    return "";
  }

  function listValue(formData, name) {
    return formData
      .getAll(name)
      .map(function (value) {
        return String(value || "").trim();
      })
      .filter(Boolean);
  }

  function listValues(formData, names) {
    return (names || [])
      .reduce(function (items, name) {
        return items.concat(listValue(formData, name));
      }, [])
      .filter(Boolean);
  }

  function boolValue(formData, name) {
    var value = formData.get(name);
    if (value === null) {
      return false;
    }
    var normalized = String(value).toLowerCase();
    return ["1", "true", "on", "yes"].indexOf(normalized) >= 0;
  }

  function normalizeSegment(value) {
    var text = String(value || "").toLowerCase();
    if (text.indexOf("vol") >= 0) {
      return "volailles";
    }
    if (text.indexOf("porc") >= 0) {
      return "porcins";
    }
    if (text.indexOf("poiss") >= 0 || text.indexOf("tilapia") >= 0) {
      return "poissons";
    }
    if (text.indexOf("bio") >= 0) {
      return "biosecurite";
    }
    if (text.indexOf("telecom") >= 0 || text.indexOf("it") >= 0 || text.indexOf("service") >= 0) {
      return "multi";
    }
    return text;
  }

  function normalizeChannel(value) {
    var text = String(value || "").toLowerCase();
    if (text.indexOf("what") >= 0) {
      return "whatsapp";
    }
    if (text.indexOf("mail") >= 0) {
      return "email";
    }
    if (text.indexOf("tel") >= 0 || text.indexOf("phone") >= 0) {
      return "appel";
    }
    return "";
  }

  function parseErrorMessage(responseData) {
    if (!responseData) {
      return "Envoi impossible. Réessayez.";
    }
    if (typeof responseData.detail === "string") {
      return responseData.detail;
    }
    var keys = Object.keys(responseData);
    if (!keys.length) {
      return "Envoi impossible. Réessayez.";
    }
    var first = responseData[keys[0]];
    if (Array.isArray(first) && first.length) {
      return String(first[0]);
    }
    if (typeof first === "string") {
      return first;
    }
    return "Envoi impossible. Vérifiez les champs.";
  }

  function showFeedback(form, type, message) {
    var selector = ".site-crm-feedback";
    var box = form.querySelector(selector);
    if (!box) {
      box = document.createElement("div");
      box.className = "alert mt-3 site-crm-feedback";
      form.appendChild(box);
    }
    box.classList.remove("alert-success", "alert-danger", "d-none");
    box.classList.add(type === "success" ? "alert-success" : "alert-danger");
    box.textContent = message;
  }

  function showKnownSuccess(form) {
    var knownIds = ["form-success", "c-success", "career-success"];
    var shown = false;
    knownIds.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) {
        el.classList.remove("d-none");
        shown = true;
      }
    });
    if (!shown) {
      showFeedback(form, "success", "Merci, votre demande a été envoyée.");
    }
  }

  function lockForm(form, isLocked) {
    var submits = form.querySelectorAll("button[type='submit'], input[type='submit']");
    submits.forEach(function (btn) {
      btn.disabled = !!isLocked;
    });
  }

  function resetWizard(form) {
    var steps = form.querySelectorAll(".step");
    if (!steps.length) {
      return;
    }
    steps.forEach(function (step, index) {
      step.classList.toggle("d-none", index !== 0);
    });

    var isContact = form.id === "c-form";
    var stepbar = document.getElementById(isContact ? "c-stepbar" : "stepbar");
    var stepLabel = document.getElementById(isContact ? "c-step-label" : "step-label");
    var prevBtn = document.getElementById(isContact ? "c-prev" : "prevBtn");
    var nextBtn = document.getElementById(isContact ? "c-next" : "nextBtn");
    var submitBtn = document.getElementById(isContact ? "c-submit" : "submitBtn");
    var waBtn = document.getElementById("waBtn");

    if (stepbar) {
      stepbar.style.width = "33%";
    }
    if (stepLabel) {
      stepLabel.textContent = "Étape 1/3 — " + (isContact ? "Besoin" : "Coordonnées");
    }
    if (prevBtn) {
      prevBtn.disabled = true;
    }
    if (nextBtn) {
      nextBtn.classList.remove("d-none");
    }
    if (submitBtn) {
      submitBtn.classList.add("d-none");
    }
    if (waBtn) {
      waBtn.classList.add("d-none");
    }
  }

  async function postJson(url, payload) {
    var response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
      credentials: "same-origin",
    });

    var data = null;
    try {
      data = await response.json();
    } catch (error) {
      data = null;
    }

    if (!response.ok) {
      throw new Error(parseErrorMessage(data));
    }
    return data;
  }

  async function postFormData(url, formData) {
    var response = await fetch(url, {
      method: "POST",
      body: formData,
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
      },
    });

    var data = null;
    try {
      data = await response.json();
    } catch (error) {
      data = null;
    }

    if (!response.ok) {
      throw new Error(parseErrorMessage(data));
    }
    return data;
  }

  function buildInboundPayload(form, kind, options) {
    var formData = new FormData(form);
    var fields = (options && options.fields) || {};
    var base = basePayload();
    var segmentRaw = firstValue(formData, fields.segment || ["species", "segment", "serviceNeed", "analysis_category", "profile"]);
    var channelRaw = firstValue(formData, fields.channel_preference || ["channel", "channel_preference"]);

    var interests = listValues(formData, fields.interests || ["interests", "specialites", "topics", "deliverables", "channels"]);

    var payload = {
      kind: kind,
      name: firstValue(formData, fields.name || ["name", "fullname", "full_name", "fullName"]),
      company: firstValue(formData, fields.company || ["company", "structure", "organisation"]),
      phone: firstValue(formData, fields.phone || ["phone", "telephone", "contactPhone"]),
      email: firstValue(formData, fields.email || ["email", "workEmail"]),
      segment: normalizeSegment(segmentRaw),
      stage: firstValue(formData, fields.stage || ["stage", "profile", "organisation", "role"]),
      intent: firstValue(formData, fields.intent || ["intent", "objective", "serviceNeed", "analysis_type"]),
      channel_preference: normalizeChannel(channelRaw),
      volume: firstValue(formData, fields.volume || ["volume", "budget"]),
      product: firstValue(formData, fields.product || ["product", "analysis_category", "format"]),
      objective: firstValue(formData, fields.objective || ["objective", "intent", "timeline", "timeline_detail"]),
      message: firstValue(formData, fields.message || ["message", "context"]),
      region: firstValue(formData, fields.region || ["region", "location"]),
      preferred_time: firstValue(formData, fields.preferred_time || ["preferred_time", "time", "timeline"]),
      interests: interests,
      consent: boolValue(formData, "consent"),
      source_page: base.source_page,
      referrer: base.referrer,
      utm_source: base.utm_source,
      utm_medium: base.utm_medium,
      utm_campaign: base.utm_campaign,
      utm_content: base.utm_content,
      utm_term: base.utm_term,
      user_agent: base.user_agent,
    };

    return payload;
  }

  function bindInboundForm(form, kind, options) {
    if (!form || form.dataset.crmBound === "1") {
      return;
    }
    form.dataset.crmBound = "1";

    form.addEventListener(
      "submit",
      async function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        if (typeof form.checkValidity === "function" && !form.checkValidity()) {
          form.classList.add("was-validated");
          return;
        }

        var payload = buildInboundPayload(form, kind, options);
        lockForm(form, true);
        try {
          await postJson(ENDPOINTS.inbound, payload);
          showKnownSuccess(form);
          form.reset();
          form.classList.remove("was-validated");
          resetWizard(form);
        } catch (error) {
          showFeedback(form, "error", error.message || "Erreur lors de l'envoi.");
        } finally {
          lockForm(form, false);
        }
      },
      true
    );
  }

  function bindCareerForm(form) {
    if (!form || form.dataset.crmBound === "1") {
      return;
    }
    form.dataset.crmBound = "1";

    form.addEventListener(
      "submit",
      async function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        if (typeof form.checkValidity === "function" && !form.checkValidity()) {
          form.classList.add("was-validated");
          return;
        }

        var source = new FormData(form);
        var base = basePayload();
        var payload = new FormData();

        payload.append("full_name", firstValue(source, ["fullname", "full_name", "name"]));
        payload.append("email", firstValue(source, ["email"]));
        payload.append("phone", firstValue(source, ["phone"]));
        payload.append("role", firstValue(source, ["role"]));
        payload.append("experience", firstValue(source, ["experience"]));
        payload.append("location", firstValue(source, ["location", "region"]));
        payload.append("availability", firstValue(source, ["availability"]));
        payload.append("mobility", firstValue(source, ["mobility"]));
        payload.append("message", firstValue(source, ["message"]));
        payload.append("consent", boolValue(source, "consent") ? "true" : "false");

        var cv = source.get("cv");
        if (cv && typeof cv === "object" && cv.name) {
          payload.append("cv", cv);
        }

        listValue(source, "specialites").forEach(function (value) {
          payload.append("specialites", value);
        });

        payload.append("source_page", base.source_page);
        payload.append("referrer", base.referrer);
        payload.append("utm_source", base.utm_source);
        payload.append("utm_medium", base.utm_medium);
        payload.append("utm_campaign", base.utm_campaign);
        payload.append("utm_content", base.utm_content);
        payload.append("utm_term", base.utm_term);
        payload.append("user_agent", base.user_agent);

        lockForm(form, true);
        try {
          await postFormData(ENDPOINTS.careers, payload);
          showKnownSuccess(form);
          form.reset();
          form.classList.remove("was-validated");

          var cvName = document.getElementById("cvName");
          if (cvName) {
            cvName.textContent = "Aucun fichier sélectionné";
          }
        } catch (error) {
          showFeedback(form, "error", error.message || "Erreur lors de l'envoi.");
        } finally {
          lockForm(form, false);
        }
      },
      true
    );
  }

  function bindNewsletterForm(form) {
    if (!form || form.dataset.crmBound === "1") {
      return;
    }
    form.dataset.crmBound = "1";

    form.addEventListener(
      "submit",
      async function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        if (typeof form.checkValidity === "function" && !form.checkValidity()) {
          form.classList.add("was-validated");
          return;
        }

        var formData = new FormData(form);
        var base = basePayload();
        var email = firstValue(formData, ["email", "newsletter_email"]);
        if (!email) {
          var emailInput = form.querySelector("input[type='email']");
          if (emailInput && emailInput.value) {
            email = String(emailInput.value).trim();
          }
        }
        var payload = {
          email: email,
          source_page: base.source_page,
          referrer: base.referrer,
          utm_source: base.utm_source,
          utm_medium: base.utm_medium,
          utm_campaign: base.utm_campaign,
          utm_content: base.utm_content,
          utm_term: base.utm_term,
          user_agent: base.user_agent,
        };

        lockForm(form, true);
        try {
          await postJson(ENDPOINTS.newsletter, payload);
          showFeedback(form, "success", "Inscription newsletter confirmée.");
          form.reset();
          form.classList.remove("was-validated");
        } catch (error) {
          showFeedback(form, "error", error.message || "Erreur lors de l'inscription.");
        } finally {
          lockForm(form, false);
        }
      },
      true
    );
  }

  function init() {
    bindInboundForm(document.getElementById("form-pro"), "lead");
    bindInboundForm(document.getElementById("c-form"), "contact");
    bindInboundForm(document.getElementById("contactForm"), "contact");
    bindInboundForm(document.getElementById("briefingForm"), "contact");
    bindInboundForm(document.getElementById("analysisRequestForm"), "contact");
    bindInboundForm(document.getElementById("reused_form"), "contact");
    document.querySelectorAll("form.theme-form-one").forEach(function (form) {
      bindInboundForm(form, "contact");
    });

    var leadForms = document.querySelectorAll("form.lead-form");
    leadForms.forEach(function (form) {
      bindInboundForm(form, "product");
    });

    bindCareerForm(document.getElementById("careerForm"));
    bindNewsletterForm(document.getElementById("newsletter-form"));
    document.querySelectorAll("form.newsletter-form, form.article-newsletter-form").forEach(function (form) {
      bindNewsletterForm(form);
    });
    bindInboundForm(document.getElementById("lead-form"), "product");

    if ("MutationObserver" in window && document.body) {
      var observer = new MutationObserver(function (records) {
        records.forEach(function (record) {
          Array.prototype.forEach.call(record.addedNodes || [], function (node) {
            if (!node || node.nodeType !== 1) {
              return;
            }

            if (node.matches && node.matches("form.lead-form")) {
              bindInboundForm(node, "product");
            }
            if (node.matches && node.matches("#lead-form")) {
              bindInboundForm(node, "product");
            }
            if (node.matches && node.matches("#newsletter-form, form.newsletter-form, form.article-newsletter-form")) {
              bindNewsletterForm(node);
            }
            if (node.matches && node.matches("#careerForm")) {
              bindCareerForm(node);
            }
            if (node.matches && node.matches("#form-pro")) {
              bindInboundForm(node, "lead");
            }
            if (node.matches && node.matches("#c-form, #contactForm, #briefingForm, #analysisRequestForm, #reused_form")) {
              bindInboundForm(node, "contact");
            }

            if (node.querySelectorAll) {
              node.querySelectorAll("form.lead-form").forEach(function (form) {
                bindInboundForm(form, "product");
              });
              node.querySelectorAll("#lead-form").forEach(function (form) {
                bindInboundForm(form, "product");
              });
              node.querySelectorAll("#newsletter-form, form.newsletter-form, form.article-newsletter-form").forEach(
                function (form) {
                  bindNewsletterForm(form);
                }
              );
              node.querySelectorAll("#careerForm").forEach(function (form) {
                bindCareerForm(form);
              });
              node.querySelectorAll("#form-pro").forEach(function (form) {
                bindInboundForm(form, "lead");
              });
              node.querySelectorAll("#c-form, #contactForm, #briefingForm, #analysisRequestForm, #reused_form").forEach(
                function (form) {
                  bindInboundForm(form, "contact");
                }
              );
            }
          });
        });
      });
      observer.observe(document.body, { childList: true, subtree: true });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
